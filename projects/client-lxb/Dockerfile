# syntax=docker/dockerfile:1

ARG NODE_VERSION=26

# --- build stage: the official Vite+ toolchain image ---
FROM ghcr.io/voidzero-dev/vite-plus:latest AS build
WORKDIR /app

# Forward encryption key to build stage so astro build validates its presence
ARG EMDASH_ENCRYPTION_KEY
ENV EMDASH_ENCRYPTION_KEY=$EMDASH_ENCRYPTION_KEY

# Copy root monorepo files and lockfile for frozen installation
COPY --chown=vp:vp package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY --chown=vp:vp projects/client-lxb/package.json projects/client-lxb/.node-version* ./projects/client-lxb/

# Install client-lxb dependencies using the frozen monorepo lockfile
RUN --mount=type=cache,id=pnpm-store,target=/home/vp/.local/share/pnpm/store,uid=1000,gid=1000 \
    vp install --filter client-lxb --frozen-lockfile

# Copy client-lxb source code
COPY --chown=vp:vp projects/client-lxb ./projects/client-lxb

# Build the Astro site (fails if EMDASH_ENCRYPTION_KEY is missing)
WORKDIR /app/projects/client-lxb
RUN vp run build

# Deploy isolated production-only dependencies for client-lxb
WORKDIR /app
# Create a new app from the pnpm monorepo to create a production-only mirror of the app
# PNPM_CONFIG_MINIMUM_RELEASE_AGE=0 skips verification of package release dates 
RUN --mount=type=cache,id=pnpm-store,target=/home/vp/.local/share/pnpm/store,uid=1000,gid=1000 \
    PNPM_CONFIG_MINIMUM_RELEASE_AGE=0 pnpm --filter client-lxb --prod deploy /app/pruned

# --- runtime stage: official node slim runtime (matches .node-version) ---
FROM node:${NODE_VERSION}-slim AS runtime
WORKDIR /app

# Install libc++, libatomic, ca-certificates, curl, and sqlite3 (for workerd sandbox, Node.js, HTTPS, healthchecks, and DB inspection)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends \
    libc++1 \
    libatomic1 \
    ca-certificates \
    curl \
    sqlite3

COPY --from=build /app/projects/client-lxb/dist ./dist
COPY --from=build /app/pruned/node_modules ./node_modules
COPY --from=build /app/projects/client-lxb/package.json ./

ENV HOST=0.0.0.0
ENV PORT=4321
ENV NODE_ENV=production
ENV EM_DATA_PATH=/app/db
ENV EM_UPLOADS_PATH=/app/uploads

RUN mkdir -p /app/db /app/uploads /app/data

EXPOSE 4321

CMD ["node", "./dist/server/entry.mjs"]