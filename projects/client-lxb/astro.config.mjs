import node from "@astrojs/node";
import partytown from "@astrojs/partytown";
import react from "@astrojs/react";
import { defineConfig } from "astro/config";
import emdash, { local, memoryCache } from "emdash/astro";
import { sqlite } from "emdash/db";
import fs from "node:fs";

const CONSTANTS = {
  EM_DATA_DIR: ".emdash/data",
};

const isProd = process.env.NODE_ENV === "production";

if (!isProd) {
  const path = `./${CONSTANTS.EM_DATA_DIR}`;
  if (!fs.existsSync(path)) {
    fs.mkdirSync(path, { recursive: true });
  }
}

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
      database: sqlite({ url: `file:./${CONSTANTS.EM_DATA_DIR}/data.db` }),
      storage: local({
        directory: `./${CONSTANTS.EM_DATA_DIR}/uploads`,
        baseUrl: "/_emdash/api/media/file",
      }),
      objectCache: memoryCache(),
      sandboxRunner: "@emdash-cms/sandbox-workerd/sandbox",
    }),
  ],
  devToolbar: { enabled: false },
});
