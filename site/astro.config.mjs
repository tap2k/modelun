import { defineConfig } from 'astro/config';

// Host-agnostic static output. Set `base`/`site` later when hosting is decided
// (e.g. base: '/atlas' for a GitHub Pages project site).
export default defineConfig({
  output: 'static',
  build: { format: 'directory' },
});
