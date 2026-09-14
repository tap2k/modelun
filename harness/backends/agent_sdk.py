"""
agent_sdk — second backend: the Claude Agent SDK, authenticated through the local Claude Code
login and billed to the Max plan (no API key).

Facts every output file stamps (see `stamp`):
  - thinking: adaptive, display "summarized" — the trace is a model-written SUMMARY, never the raw
    chain of thought. Adaptive thinking may spend zero tokens on an easy turn; `usage.thinking_tokens`
    says when it did (0 = no trace, by the model's choice, not the channel's).
  - sampling: default; temperature is refused on these models. Effort (low..max) is the knob.
  - context residual: the CLI injects the logged-in account's email, today's date and a one-line
    Agent SDK framing into every call and this adapter cannot remove them (the two switches that would, --bare and
    CLAUDE_CODE_SIMPLE, also disable OAuth). CLAUDE.md files, the working-directory block, skills,
    plugins, MCP servers, hooks and tools are all off. Verified by a context probe, 2026-09-14.

    pip install claude-agent-sdk        # plus a logged-in `claude` CLI (claude auth status)

    from backends.agent_sdk import chat, stamp
    reply, thinking, usage = chat(messages, system, max_tokens, model="claude-sonnet-5", effort="low")

Multi-turn: `messages` is the OpenAI-shaped list the runners already build. The first user turn
opens an SDK session; a later call whose prior turns match a session already seen resumes it and
sends only the new user turn, so each turn sees the real conversation history in one session.
Rate limits: the SDK reports the plan window (`resets_at`); the call sleeps until then and
retries, up to RETRIES times, rather than failing the cell.
"""

import sys
import time
import asyncio
import tempfile
import threading

from claude_agent_sdk import (query, ClaudeAgentOptions, AssistantMessage, ResultMessage,
                              TextBlock, ThinkingBlock, RateLimitEvent, SystemMessage)

EFFORTS = ("low", "medium", "high", "xhigh", "max")
THINKING = {"type": "adaptive", "display": "summarized"}   # "enabled" needs budget_tokens, which 5-gen models reject
ISOLATION_ENV = {"CLAUDE_CODE_DISABLE_ATTACHMENTS": "1", "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1",
                 "CLAUDE_CODE_DISABLE_BUNDLED_SKILLS": "1", "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"}
CONTEXT_RESIDUAL = ("Claude Code injects the account email, today's date, and a one-line framing ('a Claude agent, "
                    "built on Anthropic's Claude Agent SDK'); CLAUDE.md, cwd block, skills, plugins, MCP, hooks and tools "
                    "are off (context probe 2026-09-14, harness/backends/context_probe_2026-09-14.json)")
RETRIES = 4
MAX_WAIT = 6 * 3600          # never sleep past a five-hour window plus slack
SLUG_PREFIX = "sdk:"         # "sdk:claude-sonnet-5" selects this backend from a slug
EMPTY_CWD = tempfile.mkdtemp(prefix="agent_sdk_empty_")   # no project, no git, no CLAUDE.md

_sessions = {}               # (model, effort, system, prior-turns) -> session_id
_lock = threading.Lock()
_cli_version = None


def is_sdk_slug(slug):
    return slug.startswith(SLUG_PREFIX)


def model_of(slug):
    return slug[len(SLUG_PREFIX):] if is_sdk_slug(slug) else slug


def stamp(model_id, effort):
    """Header / per-cell provenance. model_id: a str, or {label: model_id} for a multi-model file."""
    return {"backend": "agent_sdk", "model_id": model_id, "effort": effort,
            "thinking": THINKING["type"], "thinking_display": THINKING["display"],
            "sampling": "default; temperature not settable", "context_residual": CONTEXT_RESIDUAL,
            "claude_code_version": _cli_version}


def _key(model, effort, system, turns):
    return (model, effort, system, tuple((m["role"], m["content"]) for m in turns))


class RateLimited(Exception):
    def __init__(self, resets_at, kind):
        super().__init__(f"rate limit ({kind}) resets_at={resets_at}")
        self.resets_at, self.kind = resets_at, kind


async def _one(prompt, system, max_tokens, model, effort, resume):
    global _cli_version
    opts = ClaudeAgentOptions(
        model=model, effort=effort, thinking=THINKING,
        system_prompt=system if system else "",       # "" = no system prompt (the census); never the Claude Code preset
        tools=[], allowed_tools=[], permission_mode="dontAsk", max_turns=1,
        setting_sources=[], cwd=EMPTY_CWD, resume=resume,
        env={**ISOLATION_ENV, "CLAUDE_CODE_MAX_OUTPUT_TOKENS": str(max_tokens)},
    )
    text, thinking, usage, session_id, ratelimit, err = [], [], {}, None, None, None
    async for msg in query(prompt=prompt, options=opts):
        if isinstance(msg, SystemMessage) and msg.subtype == "init":
            _cli_version = msg.data.get("claude_code_version", _cli_version)
        elif isinstance(msg, RateLimitEvent) and msg.rate_limit_info.status == "rejected":
            ratelimit = msg.rate_limit_info
        elif isinstance(msg, AssistantMessage):
            if msg.error:
                err = msg.error
            for b in msg.content:
                if isinstance(b, TextBlock):
                    text.append(b.text)
                elif isinstance(b, ThinkingBlock) and b.thinking:
                    thinking.append(b.thinking)
        elif isinstance(msg, ResultMessage):
            session_id = msg.session_id
            u = msg.usage or {}
            usage = {"input_tokens": u.get("input_tokens"), "cache_read_input_tokens": u.get("cache_read_input_tokens"),
                     "cache_creation_input_tokens": u.get("cache_creation_input_tokens"),
                     "output_tokens": u.get("output_tokens"),
                     "thinking_tokens": (u.get("output_tokens_details") or {}).get("thinking_tokens"),
                     "duration_api_ms": msg.duration_api_ms, "stop_reason": msg.stop_reason}
            if msg.is_error and not text:
                err = err or (msg.errors[0] if msg.errors else msg.result or msg.subtype)
    if ratelimit or err == "rate_limit":
        raise RateLimited(getattr(ratelimit, "resets_at", None), getattr(ratelimit, "rate_limit_type", err))
    if err and not text:
        raise RuntimeError(f"agent_sdk error: {err}")
    if not text:
        raise ValueError("empty reply from agent_sdk")
    return "".join(text), ("\n\n".join(thinking) or None), usage, session_id


def chat(messages, system, max_tokens, model, effort):
    """One turn. Returns (reply_text, thinking_summary_or_None, usage). Thread-safe (own event loop per call)."""
    assert effort in EFFORTS, effort
    turns = [m for m in messages if m["role"] != "system"]
    system = system or next((m["content"] for m in messages if m["role"] == "system"), None)
    assert turns and turns[-1]["role"] == "user", "last message must be a user turn"
    prior = turns[:-1]
    resume = None
    if prior:
        with _lock:
            resume = _sessions.get(_key(model, effort, system, prior))
        if resume is None:
            raise RuntimeError("no open session for these prior turns; a conversation must run through this adapter turn by turn")
    last = None
    for attempt in range(RETRIES):
        try:
            reply, thinking, usage, sid = asyncio.run(_one(turns[-1]["content"], system, max_tokens, model, effort, resume))
            with _lock:
                _sessions[_key(model, effort, system, turns + [{"role": "assistant", "content": reply}])] = sid
            return reply, thinking, usage
        except RateLimited as e:
            last = e
            wait = min(max((e.resets_at or 0) - time.time(), 60), MAX_WAIT) + 15
            print(f"  [agent_sdk] rate limit ({e.kind}); sleeping {wait:.0f}s then retrying ({attempt+1}/{RETRIES})",
                  file=sys.stderr, flush=True)
            time.sleep(wait)
        except (RuntimeError, ValueError) as e:
            last = e
            time.sleep(5 * (attempt + 1))
    raise last
