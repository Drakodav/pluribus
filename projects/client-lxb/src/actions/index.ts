/**
 * ============================================================================
 * ASTRO ACTIONS & BACKGROUND WORKFLOW RULES (EmDash 1.4 + Node/Docker Context)
 * ============================================================================
 *
 * WHY ACTIONS INSTEAD OF /API ROUTES?
 * - End-to-End Type Safety: Input definitions and output states autocomplete automatically.
 * - Auto-Validation: Zod schema parsing guarantees pure data before the handler executes.
 * - Secure-by-Default: Removes endpoint boilerplate, CSRF setup, and status matching.
 *
 * NON-BLOCKING ASYNC EXECUTION PRINCIPLE:
 * To keep client form submissions lightning-fast, all third-party I/O (e.g., sending
 * transactional emails, pushing webhooks) must be completely decoupled from the
 * HTTP request lifecycle.
 *
 * Rule: NEVER 'await' slow network calls (like SMTP transactions) inside the handler.
 * Instead, use Node's microtask queue (`setImmediate()`) to safely offload execution
 * onto the event loop, immediately releasing the 200 response block to the frontend.
 * ============================================================================
 */

import { defineAction } from "astro:actions";
import { z } from "zod";

export const server = {
  runTest: defineAction({
    accept: "form",
    input: z.object({
      email: z.email(),
      name: z.string(),
    }),
    handler: async (_input) => {
      return { success: true };
    },
  }),
};
