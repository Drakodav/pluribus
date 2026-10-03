# Task Tracking: client-lxb

## Active Issue: #30 [lxb] Feature: Initialize project skeleton and baseline architecture

- [x] Create project skeleton and setup `pnpm` workflow
- [x] Configure Coolify Railpack deployment compatibility (`package.json` engines & start script)
- [x] Connect Directus endpoint (`https://admin-lxb.apps.vlmd.cc/`) and `.env` template
- [x] Add companion `compose.yaml` for offline Directus testing
- [x] Create `justfile` with standard monorepo recipes and `pre-commit` target
- [x] Implement TypeScript data models (`types/directus.ts`)
- [x] Implement Directus client helper with offline fallbacks (`src/lib/directus.ts`, `src/lib/constants.ts`)
- [x] Implement shared layouts (`base-layout.astro`)
- [x] Implement core components (`navbar`, `footer`, `seasonal-hero`, `occasion-grid`, `inquiry-form`)
- [x] Implement occasion-first routes (`/`, `/occasions`, `/occasions/[slug]`, `/gallery`, `/pricing`, `/book`, `/balloon-care`, `/contact`)
- [x] Add `projects/client-lxb/CONTEXT.md` and link in root `CONTEXT-MAP.md`
- [x] Verify `just check` and `just build` pass with zero errors
