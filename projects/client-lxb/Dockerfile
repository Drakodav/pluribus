# syntax=docker/dockerfile:1

# --- build stage: the official Vite+ toolchain image ---
FROM ghcr.io/voidzero-dev/vite-plus:latest AS build
WORKDIR /app

# Forward encryption key to build stage so astro build validates its presence
ARG EMDASH_ENCRYPTION_KEY
ENV EMDASH_ENCRYPTION_KEY=$EMDASH_ENCRYPTION_KEY

# Install dependencies first so this layer is cached across source changes
COPY --chown=vp:vp package.json pnpm-lock.yaml* pnpm-workspace.yaml* .node-version* ./
RUN if [ -f pnpm-lock.yaml ]; then vp install --frozen-lockfile; else vp install; fi

# Build the Astro site (fails if EMDASH_ENCRYPTION_KEY is missing)
COPY --chown=vp:vp . .
RUN vp run build

# Export the exact resolved Node.js binary for the runtime stage
RUN cp "$(vp env which node | head -1)" /tmp/node

# --- runtime stage: minimal glibc debian runtime ---
FROM debian:bookworm-slim AS runtime
WORKDIR /app

# Install libc++, ca-certificates, and curl (required for workerd plugin sandbox, HTTPS, and healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libc++1 \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# The exact Node.js binary resolved by Vite+ from .node-version
COPY --from=build /tmp/node /usr/local/bin/node

COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/package.json ./

ENV HOST=0.0.0.0
ENV PORT=4321
ENV NODE_ENV=production
ENV EM_DATA_PATH=/app/data

RUN mkdir -p /app/data /app/data/uploads

EXPOSE 4321
CMD ["node", "./dist/server/entry.mjs"]