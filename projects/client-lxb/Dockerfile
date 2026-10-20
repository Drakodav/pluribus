# syntax=docker/dockerfile:1

# --- build stage: the official Vite+ toolchain image ---
FROM ghcr.io/voidzero-dev/vite-plus:latest AS build
WORKDIR /app

# Install dependencies first so this layer is cached across source changes
COPY --chown=vp:vp package.json pnpm-lock.yaml* pnpm-workspace.yaml* .node-version* ./
RUN if [ -f pnpm-lock.yaml ]; then vp install --frozen-lockfile; else vp install; fi

# Build the Astro site
COPY --chown=vp:vp . .
RUN vp run build

# Export the exact resolved Node.js binary for the runtime stage
RUN cp "$(vp env which node | head -1)" /tmp/node

# --- deps stage: production-only dependencies ---
FROM ghcr.io/voidzero-dev/vite-plus:latest AS deps
WORKDIR /app
COPY --chown=vp:vp package.json pnpm-lock.yaml* pnpm-workspace.yaml* .node-version* ./
RUN if [ -f pnpm-lock.yaml ]; then vp install --frozen-lockfile --prod; else vp install --prod; fi

# --- runtime stage: minimal glibc debian runtime ---
FROM debian:bookworm-slim AS runtime
WORKDIR /app

# Install libc++ and ca-certificates (required for workerd plugin sandbox & outbound HTTPS)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libc++1 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# The exact Node.js binary resolved by Vite+ from .node-version
COPY --from=build /tmp/node /usr/local/bin/node

COPY --from=build /app/dist ./dist
COPY --from=deps /app/node_modules ./node_modules
COPY --from=build /app/package.json ./

ENV HOST=0.0.0.0
ENV PORT=4321
ENV NODE_ENV=production
ENV EM_DATA_PATH=/app/data

RUN mkdir -p /app/data /app/data/uploads

EXPOSE 4321
CMD ["node", "./dist/server/entry.mjs"]