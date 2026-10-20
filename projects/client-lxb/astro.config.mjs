import node from "@astrojs/node";
import partytown from "@astrojs/partytown";
import react from "@astrojs/react";
import { defineConfig } from "astro/config";
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
  EM_DATA_PATH: z.string().default(".emdash/data"),
  EMDASH_ENCRYPTION_KEY: z
    .string({
      required_error: "EMDASH_ENCRYPTION_KEY is required",
      invalid_type_error: "EMDASH_ENCRYPTION_KEY must be a string",
    })
    .min(1, "EMDASH_ENCRYPTION_KEY cannot be empty"),
});

const env = envSchema.parse(process.env);

const isDbFile = env.EM_DATA_PATH.endsWith(".db");
const dataDir = isDbFile ? path.dirname(env.EM_DATA_PATH) : env.EM_DATA_PATH;
const dbFile = isDbFile ? env.EM_DATA_PATH : path.join(env.EM_DATA_PATH, "data.db");
const uploadsDir = path.join(dataDir, "uploads");

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
