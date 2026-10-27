import node from "@astrojs/node";
import partytown from "@astrojs/partytown";
import react from "@astrojs/react";
import { defineConfig, memoryCache as astroCache } from "astro/config";
import emdash, { local, memoryCache } from "emdash/astro";
import { sqlite } from "emdash/db";
import fs from "node:fs";
import path from "node:path";
import { z } from "zod";

if (typeof process.loadEnvFile === "function" && fs.existsSync(".env")) {
  process.loadEnvFile(".env");
}

const envSchema = z.object({
  NODE_ENV: z.enum(["development", "production", "test"]).default("development"),
  EM_DATA_PATH: z.string().optional(),
  EM_DB_PATH: z.string().optional(),
  EM_UPLOADS_PATH: z.string().optional(),
  EMDASH_SITE_URL: z.string().optional(),
  SITE_URL: z.string().optional(),
  COOLIFY_URL: z.string().optional(),
  COOLIFY_FQDN: z.string().optional(),
  EMDASH_ENCRYPTION_KEY: z
    .string({
      required_error: "EMDASH_ENCRYPTION_KEY is required",
      invalid_type_error: "EMDASH_ENCRYPTION_KEY must be a string",
    })
    .min(1, "EMDASH_ENCRYPTION_KEY cannot be empty"),
});

const env = envSchema.parse(process.env);

const isProd = env.NODE_ENV === "production";
const defaultDbPath = isProd ? "/app/db" : ".emdash/data";
const rawDbPath = env.EM_DB_PATH || env.EM_DATA_PATH || defaultDbPath;
const isDbFile = rawDbPath.endsWith(".db");
const dataDir = isDbFile ? path.dirname(rawDbPath) : rawDbPath;
const dbFile = isDbFile ? rawDbPath : path.join(rawDbPath, "data.db");
const defaultUploadsDir = isProd ? "/app/uploads" : path.join(dataDir, "uploads");
const uploadsDir = env.EM_UPLOADS_PATH || defaultUploadsDir;

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

if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
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
    }),
  ],
  devToolbar: { enabled: false },
});
