import fs from 'node:fs';
import path from 'node:path';
import { getCollection } from 'astro:content';
import type { AstroGlobal } from 'astro';

export const SITE_TITLE = 'Modeling notebook';

const base = import.meta.env.BASE_URL.replace(/\/$/, '');
/** Prefix a root-relative path with the deploy base. */
export const url = (p: string) => base + p;

/** Project slug for a component: explicit prop, else the page being rendered. */
export function projectOf(astro: AstroGlobal, prop?: string): string {
  const slug = prop ?? astro.locals.project;
  if (!slug) throw new Error('No project in scope: pass project="<slug>"');
  return slug;
}

/** Read a generated JSON file from public/data/<project>/..., or throw with the fix. */
export function readData<T>(project: string, ...rel: string[]): T {
  const file = path.join(process.cwd(), 'public', 'data', project, ...rel);
  if (!fs.existsSync(file)) {
    throw new Error(`Missing ${path.relative(process.cwd(), file)} — run \`make build\` (or \`uv run modelkit build ${project}\`) first.`);
  }
  return JSON.parse(fs.readFileSync(file, 'utf8')) as T;
}

export const dataUrl = (project: string, ...rel: string[]) => url(['/data', project, ...rel].join('/'));

export interface PageLink {
  slug: string;   // "" for a project's first page
  num: string;    // "01"
  title: string;
  summary: string;
  href: string;
  entry: Awaited<ReturnType<typeof getCollection<'pages'>>>[number];
}

/** A project's pages in filename order. The first one is served at /<project>/. */
export async function pagesOf(project: string): Promise<PageLink[]> {
  const all = await getCollection('pages', (p) => p.id.startsWith(project + '/pages/') && !p.data.draft);
  return all
    .sort((a, b) => a.id.localeCompare(b.id))
    .map((entry, i) => {
      const name = entry.id.split('/').pop()!.replace(/^\d+-/, '');
      const slug = i === 0 ? '' : name;
      return {
        slug,
        num: String(i + 1).padStart(2, '0'),
        title: entry.data.title,
        summary: entry.data.summary,
        href: url(`/${project}/${slug ? slug + '/' : ''}`),
        entry,
      };
    });
}

export interface PartInfo {
  id: string; name: string; source: string; material: string | null; mpn: string; color: string;
  mass_g: number | null; mass_from: string; size_mm: number[]; explode_mm: number[];
  description: string; notes: string[]; files: Record<'glb' | 'stl' | 'step', string>;
  layer?: string;
}
export interface Manifest {
  project: string; name: string; title: string; description: string;
  size_mm: number[]; mass_g: number; assembly_step: string; parts: PartInfo[];
}
export interface SimData {
  name: string; title: string; x_label: string; y_label: string;
  x: number[]; series: { name: string; y: number[] }[]; params: Record<string, unknown>;
}

export const grams = (g: number | null) => (g == null ? '—' : g >= 100 ? g.toFixed(0) + ' g' : g.toFixed(1) + ' g');
