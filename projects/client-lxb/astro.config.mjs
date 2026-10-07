// @ts-check
import { defineConfig } from 'astro/config';

import node from '@astrojs/node';

import partytown from '@astrojs/partytown';
import react from '@astrojs/react';

// https://astro.build/config
export default defineConfig({
  output: 'static',

  server: {
    host: '0.0.0.0',
    port: 4321,
  },

  adapter: node({
    mode: 'standalone',
  }),

  integrations: [partytown(), react({compiler: true})],
});