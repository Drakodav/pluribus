/**
 * ============================================================================
 * ASTRO ACTIONS REGISTRY
 * ============================================================================
 * Central actions entrypoint. Handlers are decoupled into dedicated modules
 * for separation of concerns and maintainability.
 * ============================================================================
 */

import { submitInquiry } from "./submit-inquiry";

export const server = {
  submitInquiry,
};
