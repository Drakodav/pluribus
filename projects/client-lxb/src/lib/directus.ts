import {
  createDirectus,
  rest,
  staticToken,
  readItems,
  createItem,
} from "@directus/sdk";
import type {
  DirectusSchema,
  Occasion,
  Product,
  SeasonalBanner,
  Inquiry,
} from "../types/directus";
import {
  DEFAULT_OCCASIONS,
  DEFAULT_PRODUCTS,
  DEFAULT_SEASONAL_BANNER,
} from "./constants";

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
 * Fetch all active occasions from Directus SDK, falling back to static defaults
 * if Directus collections or public permissions are not yet configured.
 */
export async function getOccasions(): Promise<Occasion[]> {
  // try {
  //   const items = await directus.request(
  //     readItems("occasions", {
  //       fields: ["*"],
  //     }),
  //   );
  //   if (items && Array.isArray(items) && items.length > 0) {
  //     return items as Occasion[];
  //   }
  // } catch (error) {
  //   console.warn(
  //     "[directus-sdk] Occasions collection unavailable, using fallback data:",
  //     error,
  //   );
  // }
  return DEFAULT_OCCASIONS;
}

/**
 * Fetch products via Directus SDK, optionally filtered by occasion slug
 */
export async function getProducts(occasionSlug?: string): Promise<Product[]> {
  // try {
  //   const items = await directus.request(
  //     readItems("products", {
  //       fields: ["*"],
  //     }),
  //   );
  //   if (items && Array.isArray(items) && items.length > 0) {
  //     const typed = items as Product[];
  //     if (occasionSlug) {
  //       return typed.filter((p) => p.occasion_slugs?.includes(occasionSlug));
  //     }
  //     return typed;
  //   }
  // } catch (error) {
  //   console.warn(
  //     "[directus-sdk] Products collection unavailable, using fallback data:",
  //     error,
  //   );
  // }

  // if (occasionSlug) {
  //   return DEFAULT_PRODUCTS.filter((p) =>
  //     p.occasion_slugs?.includes(occasionSlug),
  //   );
  // }
  return DEFAULT_PRODUCTS;
}

/**
 * Fetch active seasonal banner spotlight via Directus SDK
 */
export async function getSeasonalBanner(): Promise<SeasonalBanner> {
  // try {
  //   const items = await directus.request(
  //     readItems("seasonal_banners", {
  //       filter: { is_active: { _eq: true } },
  //       limit: 1,
  //     }),
  //   );
  //   if (items && Array.isArray(items) && items.length > 0) {
  //     return items[0] as SeasonalBanner;
  //   }
  // } catch (error) {
  //   console.warn(
  //     "[directus-sdk] Seasonal banners collection unavailable, using fallback:",
  //     error,
  //   );
  // }
  return DEFAULT_SEASONAL_BANNER;
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
