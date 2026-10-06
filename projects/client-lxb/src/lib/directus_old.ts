import { createDirectus, rest, staticToken } from "@directus/sdk";
import type { DirectusSchema, Inquiry } from "../types/directus_old";

const DIRECTUS_URL =
  import.meta.env.DIRECTUS_URL || "https://admin-lxb.apps.vlmd.cc";
const DIRECTUS_TOKEN = import.meta.env.DIRECTUS_TOKEN;

// Initialize the Directus SDK client
const baseClient = createDirectus<DirectusSchema>(DIRECTUS_URL).with(rest());

export const directus = DIRECTUS_TOKEN
  ? baseClient.with(staticToken(DIRECTUS_TOKEN))
  : baseClient;

/**
 * Helper to construct full URL for Directus uploaded assets
 */
export function getAssetUrl(
  fileId?: string,
  options?: { width?: number; height?: number; quality?: number; fit?: string },
): string {
  if (!fileId) return "/placeholders/balloon-placeholder.svg";
  const url = new URL(`/assets/${fileId}`, DIRECTUS_URL);
  if (options) {
    if (options.width) url.searchParams.set("width", String(options.width));
    if (options.height) url.searchParams.set("height", String(options.height));
    if (options.quality)
      url.searchParams.set("quality", String(options.quality));
    if (options.fit) url.searchParams.set("fit", options.fit);
  }
  return url.toString();
}

/**
 * Submit an inquiry to Directus via SDK
 */
export async function submitInquiry(
  inquiry: Inquiry,
): Promise<{ success: boolean; id?: string | number; error?: string }> {
  // try {
  //   const created = await directus.request(
  //     createItem('inquiries', {
  //       ...inquiry,
  //       status: 'new',
  //     })
  //   );
  //   return { success: true, id: (created as Inquiry)?.id };
  // } catch (error: any) {
  //   console.error('[directus-sdk] Failed to submit inquiry:', error);
  //   return { success: false, error: error?.message || 'Submission failed' };
  // }
  return { success: false, error: "Submission failed" };
}
