import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';

// SITE_BASE is set by the Pages workflow (e.g. /modeling-repo); local dev serves from /.
export default defineConfig({
  site: process.env.SITE_URL,
  base: process.env.SITE_BASE || '/',
  trailingSlash: 'always',
  integrations: [mdx()],
  vite: { server: { fs: { allow: ['..'] } } },
});
