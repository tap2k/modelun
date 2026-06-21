import atlas from '../data/atlas.json';

export const MODELS = atlas.models;
export const GROUP_DEFS = atlas.group_defs;
export const SCRIPT_VERSION = atlas.script_version;
export const SYSTEM_PROMPT = atlas.system_prompt;

export function getModel(slug) {
  return MODELS.find((m) => m.slug === slug);
}

// Display name for the provider/lab that ships a model, keyed off the route org
// prefix (anthropic/…). gpt-3.5-turbo-instruct has no prefix, so fall back to slug.
const FAMILY_NAMES = {
  anthropic: 'Anthropic',
  openai: 'OpenAI',
  google: 'Google',
  'meta-llama': 'Meta',
  mistralai: 'Mistral',
  'x-ai': 'xAI',
  qwen: 'Qwen',
  deepseek: 'DeepSeek',
  cohere: 'Cohere',
  moonshotai: 'Moonshot',
  nousresearch: 'Nous Research',
  gryphe: 'Gryphe',
};

function familyOf(m) {
  const org = m.route.includes('/') ? m.route.split('/')[0] : null;
  if (org && FAMILY_NAMES[org]) return FAMILY_NAMES[org];
  if (m.slug.startsWith('gpt')) return 'OpenAI';
  return org || m.slug;
}

// Recency proxy: no release dates in the data, so use the first version number in
// the slug (claude-3.5-haiku → 3.5, gpt-5.4 → 5.4). Comparable within a family,
// not across families. Returns -1 when a slug carries no version (single-member
// families where ordering is moot).
function versionOf(m) {
  const match = m.slug.match(/(\d+(?:\.\d+)?)/);
  return match ? parseFloat(match[1]) : -1;
}

// Models grouped by provider family, families alphabetical, members newest-first.
export function modelsByFamily() {
  const families = new Map();
  for (const m of MODELS) {
    const fam = familyOf(m);
    if (!families.has(fam)) families.set(fam, []);
    families.get(fam).push(m);
  }
  return [...families.entries()]
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([family, models]) => ({
      family,
      models: models.sort(
        (a, b) => versionOf(b) - versionOf(a) || b.slug.localeCompare(a.slug)
      ),
    }));
}

// Models grouped by their primary bestiary group, in the canonical group order.
export function modelsByGroup() {
  const order = Object.keys(GROUP_DEFS);
  const out = order.map((g) => ({
    group: g,
    desc: GROUP_DEFS[g],
    models: MODELS.filter((m) => m.group?.primary === g).sort((a, b) =>
      a.slug.localeCompare(b.slug)
    ),
  }));
  return out;
}
