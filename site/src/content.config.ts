import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

// Content lives beside the models, in ../projects/<slug>/.
const base = '../projects';
const slugOf = ({ entry }: { entry: string }) => entry.split('/')[0];

const projects = defineCollection({
  loader: glob({ base, pattern: '*/project.yaml', generateId: slugOf }),
  schema: z.object({
    title: z.string(),
    summary: z.string().default(''),
    status: z.enum(['concept', 'modeled', 'prototyped', 'tested']).default('concept'),
    order: z.number().default(100),
  }),
});

const pages = defineCollection({
  // id: "<slug>/pages/NN-name"
  loader: glob({ base, pattern: '*/pages/*.mdx', generateId: ({ entry }) => entry.replace(/\.mdx$/, '') }),
  schema: z.object({
    title: z.string(),
    summary: z.string().default(''),
    draft: z.boolean().default(false),
  }),
});

const boms = defineCollection({
  loader: glob({ base, pattern: '*/bom.yaml', generateId: slugOf }),
  schema: z.object({
    currency: z.string().default('USD'),
    items: z.array(
      z.object({
        ref: z.string(),
        description: z.string(),
        qty: z.number().default(1),
        manufacturer: z.string().nullish(),
        mpn: z.string().nullish(),
        supplier: z.string().nullish(),
        url: z.string().nullish(),
        unit_cost: z.number().nullish(),
        notes: z.string().nullish(),
      }),
    ),
  }),
});

export const collections = { projects, pages, boms };
