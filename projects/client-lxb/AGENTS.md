This is an EmDash site -- a CMS built on Astro with a full admin UI.

## Commands

```bash
pnpm dev              # Start the Astro dev server
npx emdash types      # Regenerate TypeScript types from a running site
```

The admin UI is at `http://localhost:4321/_emdash/admin`.

## Key Files

| File                     | Purpose                                                                            |
| ------------------------ | ---------------------------------------------------------------------------------- |
| `astro.config.mjs`       | Astro config with `emdash()` integration, database, and storage                    |
| `src/live.config.ts`     | EmDash loader registration (boilerplate -- don't modify)                           |
| `seed/seed.json`         | Schema definition + demo content (collections, fields, taxonomies, menus, widgets) |
| `emdash-env.d.ts`        | Generated types for collections (auto-regenerated on dev server start)             |
| `src/layouts/Base.astro` | Base layout with EmDash wiring (menus, search, page contributions)                 |
| `src/pages/`             | Astro pages -- all server-rendered                                                 |

## Skills

Agent skills are in `.agents/skills/`. Load them when working on specific tasks:

- **building-emdash-site** -- Querying content, rendering Portable Text, schema design, seed files, site features (menus, widgets, search, SEO, comments, bylines). Start here.
- **creating-plugins** -- Building EmDash plugins with hooks, storage, admin UI, API routes, and Portable Text block types.
- **emdash-cli** -- CLI commands for content management, seeding, type generation, and visual editing flow.

## Documentation

The EmDash docs are available as an MCP server at `https://docs.emdashcms.com/mcp`. When you need to verify an API, hook, config option, field type, or pattern, call `search_docs` against the live documentation rather than relying on training-data recall. The docs reflect current behaviour; assumptions may not.

This template ships with `.mcp.json`, `.cursor/mcp.json`, and `.vscode/mcp.json` so Claude Code, Cursor, and VS Code auto-discover the docs server. Other tools (OpenCode, Windsurf, etc.) need a manual one-time setup -- see [docs.emdashcms.com/docs-mcp](https://docs.emdashcms.com/docs-mcp).

## Rules

- All content pages must be server-rendered (`output: "server"`). No `getStaticPaths()` for CMS content.
- Image fields are objects (`{ src, alt }`), not strings. Use `<Image image={...} />` from `"emdash/ui"`.
- `entry.id` is the slug (for URLs). `entry.data.id` is the database ULID (for API calls like `getEntryTerms`).
- When Astro's cache is enabled, pass content-query hints to `Astro.cache.set(cacheHint)`. Use the `WithCacheHint` variants for site settings, menus, taxonomies, and widget areas rendered by cached routes.
- Taxonomy names in queries must match the seed's `"name"` field exactly (e.g., `"category"` not `"categories"`).

## Development

When starting the dev server, use background mode:

```
astro dev --background
```

Manage the background server with `astro dev stop`, `astro dev status`, and `astro dev logs`.

## Documentation

Full documentation: https://docs.astro.build

Consult these guides before working on related tasks:

- [Adding pages, dynamic routes, or middleware](https://docs.astro.build/en/guides/routing/)
- [Working with Astro components](https://docs.astro.build/en/basics/astro-components/)
- [Using React, Vue, Svelte, or other framework components](https://docs.astro.build/en/guides/framework-components/)
- [Adding or managing content](https://docs.astro.build/en/guides/content-collections/)
- [Adding styles or using Tailwind](https://docs.astro.build/en/guides/styling/)
- [Supporting multiple languages](https://docs.astro.build/en/guides/internationalization/)

## Schema

- `pages` collection: `title`, `content` (a first-class `blocks` field). Its `/{slug}` URL pattern drives admin links, previews, and the sitemap; `src/pages/home.astro` redirects `/home` to `/`, keeping the query string so Home's preview links work.
- No taxonomies.
- Four menus: `primary` (the header links), plus `footer_product`, `footer_company`, and `footer_support` (the footer's Product, Company, and Support columns). The seeded links point at home page sections (`/#platform`, `/#monitoring`, `/#planning`, `/#customers`, `/#faq`), the pricing and contact pages, and `mailto:` addresses. A `primary` item with the CSS class `button` renders as a header button instead of a link (the seeded Book a demo item); on narrow screens only the first button stays in the header and the rest move into the menu. Each footer column's heading is its menu's label. Only the `button` class has an effect. Change menu labels and item classes in the admin's menu editor: the pencil button next to a menu's title renames it, and an item's **CSS classes** field sets its classes. The MCP `menu_update` and `menu_set_items` tools change them too. Applying the seed to an existing site doesn't rename menus that already exist.

Site settings have `title` and `tagline`. The title renders as the serif wordmark in the header and footer (a logo set in site settings replaces it there) and as the giant cropped wordmark at the bottom of every page; an empty title shows "My Site". The tagline renders in the footer when set.

Each page's meta description is its SEO panel description, else the subheadline of its first hero, else the tagline. Its share image is the SEO panel image, else the first hero's photo, else the default social image from site settings. The home page is titled after the site unless its SEO panel sets a title. Browser titles join the page and site titles with the title separator from Settings › SEO, which the seed sets to an em dash (also the default when it's unset).

## What not to do

- Don't write stock SaaS copy: "Build products people actually want", "Elevate your workflow", "The all-in-one platform for modern teams". These are placeholders. Write what the product actually does, for whom, with one specific outcome.
- Don't draw structure with lines: no hairline rules between sections, bordered logo or feature grids, or divided stats, FAQ rows, and checklists. Space, cards, and sheets separate content in this design.
- Don't spread the accent colour onto buttons, panels, or headlines. It marks the quote mark; on everything, it stops signalling.
- Don't use stock portraits for fictional people. Leave testimonial avatars empty so initials show, and add photos only of real customers who agreed to be quoted.
- Don't ship more than three pricing tiers. Three is the default for a reason -- more makes choice harder, not easier -- and the pricing block allows no more.
- Don't put sentences in stat values. A value is a short figure (`23%`, `4,800`, `9 mo`); the label carries the explanation.
- Don't add a hero block followed immediately by another hero block. One hero, then the other blocks in any order.
- Don't add JavaScript animation or motion that ignores `prefers-reduced-motion`. Every animation here is CSS and stops when the reader asks for reduced motion.
- Don't replace the `marketing_pricing` block with a hand-coded table. The block is the data shape downstream renderers expect.
