import atlas from '../data/atlas.json';

export const MODELS = atlas.models;
export const GROUP_DEFS = atlas.group_defs;
export const SCRIPT_VERSION = atlas.script_version;
export const SYSTEM_PROMPT = atlas.system_prompt;

export function getModel(slug) {
  return MODELS.find((m) => m.slug === slug);
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
