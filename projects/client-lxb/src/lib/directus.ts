import {
  createDirectus,
  rest,
  staticToken,
  readItem,
  readItems,
  createItem,
  readSingleton,
  type DirectusClient,
  type RestClient,
  type RestCommand,
} from "@directus/sdk";
import type { Schema } from "../types/directus";

type DClient = DirectusClient<Schema> & RestClient<Schema>;

class DirectusManager {
  static #instance: DirectusManager;
  #cache = new Map<string, Promise<unknown>>();

  private client: DClient;

  private constructor() {
    const DIRECTUS_URL =
      import.meta.env.DIRECTUS_URL || "https://admin-lxb.apps.vlmd.cc";
    const DIRECTUS_TOKEN = import.meta.env.DIRECTUS_TOKEN;

    const baseClient = createDirectus<Schema>(DIRECTUS_URL).with(rest());

    this.client = DIRECTUS_TOKEN
      ? baseClient.with(staticToken(DIRECTUS_TOKEN))
      : baseClient;
  }

  public static get instance(): DirectusManager {
    if (!DirectusManager.#instance) {
      DirectusManager.#instance = new DirectusManager();
    }

    return DirectusManager.#instance;
  }

  private async cached<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
    const existing = this.#cache.get(key);
    if (existing) {
      return existing as Promise<T>;
    }
    const promise = fetcher().catch((error) => {
      // Don't poison the cache with rejected requests
      this.#cache.delete(key);
      throw error;
    });
    this.#cache.set(key, promise);
    return promise;
  }

  public clearCache(key?: string) {
    if (key) {
      this.#cache.delete(key);
    } else {
      this.#cache.clear();
    }
  }

  async getSiteSettings() {
    try {
      const result = await this.request(
        readSingleton("site_settings", { fields: ["*"] }),
        "site_settings",
      );
      return result ?? null;
    } catch (err) {
      console.warn("[directus] Failed to fetch site_settings:", err);
      return null;
    }
  }

  async getOccasions() {
    try {
      const result = await this.request(
        readItems("occasion", { fields: ["*"] }),
        "occasions",
      );
      return result || [];
    } catch (err) {
      console.warn("[directus] Failed to fetch occasions:", err);
      return [];
    }
  }

  async getSeasonalBanners() {
    try {
      const result = await this.request(
        readItems("seasonal_banners", { fields: ["*"] }),
        "seasonal_banners",
      );
      return result || [];
    } catch (err) {
      console.warn("[directus] Failed to fetch seasonal_banners:", err);
      return [];
    }
  }

  async getProducts() {
    try {
      const result = await this.request(
        readItems("products", { fields: ["*"] }),
        "products",
      );
      return result || [];
    } catch (err) {
      console.warn("[directus] Failed to fetch products:", err);
      return [];
    }
  }

  /**
   * Execute any Directus REST command with full type inference for Output and Schema.
   * Optionally pass a cacheKey to cache the resulting Promise.
   */
  async request<Output>(
    command: RestCommand<Output, Schema>,
    cacheKey?: string,
  ): Promise<Output> {
    if (cacheKey) {
      return this.cached(cacheKey, () => this.client.request(command));
    }
    return this.client.request(command);
  }

  public get rawClient(): DClient {
    return this.client;
  }
}

const dClient = DirectusManager.instance;

export { dClient };
