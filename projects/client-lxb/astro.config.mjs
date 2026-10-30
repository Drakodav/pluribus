import node from "@astrojs/node";
import partytown from "@astrojs/partytown";
import react from "@astrojs/react";
import { defineConfig, memoryCache as astroCache } from "astro/config";
import emdash, { local, memoryCache } from "emdash/astro";
import { sqlite } from "emdash/db";
import fs from "node:fs";
import path from "node:path";
import { z } from "zod";
import { emdashSmtp } from "emdash-smtp";
import tailwindcss from "@tailwindcss/vite";

if (typeof process.loadEnvFile === "function" && fs.existsSync(".env")) {
  process.loadEnvFile(".env");
}

const envSchema = z.object({
  NODE_ENV: z.enum(["development", "production", "test"]).default("development"),
  EMDASH_SITE_URL: z.string().optional(),
  SITE_URL: z.string().optional(),
  COOLIFY_URL: z.string().optional(),
  COOLIFY_FQDN: z.string().optional(),
  EMDASH_ENCRYPTION_KEY: z.string().optional(),
});

const env = envSchema.parse(process.env);

const isBuild = process.env.npm_lifecycle_event === "build" || process.argv.includes("build");
if (!isBuild && env.NODE_ENV === "production" && !env.EMDASH_ENCRYPTION_KEY) {
  throw new Error("EMDASH_ENCRYPTION_KEY is required in production");
}

const isProd = env.NODE_ENV === "production" && !!env.COOLIFY_URL;
const rawDbPath = isProd ? "/app/db" : ".emdash/data";
const isDbFile = rawDbPath.endsWith(".db");
const dataDir = isDbFile ? path.dirname(rawDbPath) : rawDbPath;
const dbFile = isDbFile ? rawDbPath : path.join(rawDbPath, "data.db");
const uploadsDir = isProd ? "/app/uploads" : path.join(dataDir, "uploads");

const candidateUrl = [
  env.EMDASH_SITE_URL,
  env.SITE_URL,
  env.COOLIFY_URL,
  env.COOLIFY_FQDN ? `https://${env.COOLIFY_FQDN}` : undefined,
]
  .map((url) => url?.trim())
  .find(Boolean);

const siteUrl = candidateUrl
  ? (candidateUrl.startsWith("http") ? candidateUrl : `https://${candidateUrl}`).replace(/\/+$/, "")
  : undefined;

if (!isProd) {
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
  }
  if (!fs.existsSync(uploadsDir)) {
    fs.mkdirSync(uploadsDir, { recursive: true });
  }
}

const sqliteUrl = `file:${dbFile.startsWith("/") ? "" : "./"}${dbFile.replace(/^\.\//, "")}`;
const storageDir = uploadsDir.startsWith("/") ? uploadsDir : `./${uploadsDir.replace(/^\.\//, "")}`;

export default defineConfig({
  output: "server",
  cache: {
    provider: astroCache(),
  },
  server: {
    host: "0.0.0.0",
    port: 4321,
  },
  adapter: node({
    mode: "standalone",
  }),
  image: {
    layout: "constrained",
    responsiveStyles: true,
  },
  integrations: [
    partytown(),
    react({ compiler: true }),
    emdash({
      siteUrl,
      updateCheck: true,
      database: sqlite({ url: sqliteUrl }),
      storage: local({
        directory: storageDir,
        baseUrl: "/_emdash/api/media/file",
      }),
      objectCache: memoryCache(),
      sandboxRunner: "@emdash-cms/sandbox-workerd/sandbox",
      plugins: [emdashSmtp()],
    }),
  ],
  vite: {
    plugins: [tailwindcss()],
  },
  devToolbar: { enabled: false },
});
