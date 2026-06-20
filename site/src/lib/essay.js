import { marked } from 'marked';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { MODELS } from './atlas.js';

const ESSAY_PATH = fileURLToPath(new URL('../../../docs/essay.md', import.meta.url));

// Map an essay display-name (e.g. "GPT-4-turbo", "Claude 3 Haiku") to a model slug.
function nameToSlug(name) {
  const n = name.toLowerCase().replace(/[^a-z0-9]/g, '');
  for (const m of MODELS) {
    const s = m.slug.toLowerCase().replace(/[^a-z0-9]/g, '');
    if (s === n) return m.slug;
  }
  // looser: essay drops date suffixes / uses spaces (e.g. "gpt-4o-mini")
  for (const m of MODELS) {
    const s = m.slug.toLowerCase().replace(/[^a-z0-9]/g, '');
    if (s.startsWith(n) && n.length >= 5) return m.slug;
  }
  return null;
}

export function renderEssay() {
  const md = readFileSync(ESSAY_PATH, 'utf8');
  let html = marked.parse(md);

  // Link **Model** bolds to their pages (only when the bold resolves to a slug).
  html = html.replace(/<strong>([^<]+)<\/strong>/g, (m, name) => {
    const slug = nameToSlug(name.trim());
    return slug
      ? `<strong><a class="model-link" href="/model/${slug}/">${name}</a></strong>`
      : m;
  });

  return html;
}
