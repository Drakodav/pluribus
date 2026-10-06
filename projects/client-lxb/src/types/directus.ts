import type { DirectusUser, DirectusFile } from "@directus/sdk"

export type Schema = {
  inquiry: Inquiry[];
  occasion: Occasion[];
  products: Product[];
  seasonal_banners: SeasonalBanner[];
  site_settings: SiteSettings;
  directus_deployments: CustomDirectusDeployment;
}

export type Inquiry = {
  id: string;
  archived: boolean;
  sort: number | null;
  user_created: string | DirectusUser<Schema> | null;
  date_created: "datetime" | null;
  user_updated: string | DirectusUser<Schema> | null;
  date_updated: "datetime" | null;
  email: string | null;
}

export type Occasion = {
  id: string;
  archived: boolean;
  sort: number | null;
  user_created: string | DirectusUser<Schema> | null;
  date_created: "datetime" | null;
  user_updated: string | DirectusUser<Schema> | null;
  date_updated: "datetime" | null;
  title: string | null;
  subtitle: string | null;
  description: string | null;
  badge: string | null;
  starting_price: string | null;
  highlights: Array<string> | null;
  slug: string | null;
}

export type Product = {
  id: string;
  archived: boolean;
  sort: number | null;
  user_created: string | DirectusUser<Schema> | null;
  date_created: "datetime" | null;
  user_updated: string | DirectusUser<Schema> | null;
  date_updated: "datetime" | null;
  name: string | null;
  subtitle: string | null;
  starting_price: string | null;
  description: string | null;
  features: Array<string> | null;
  slug: string | null;
}

export type SeasonalBanner = {
  id: string;
  archived: boolean;
  sort: number | null;
  user_created: string | DirectusUser<Schema> | null;
  date_created: "datetime" | null;
  user_updated: string | DirectusUser<Schema> | null;
  date_updated: "datetime" | null;
  name: string | null;
  sub_title: string | null;
  title: string | null;
  cta_text: string | null;
  badge: string | null;
  is_active: boolean;
  slug: string | null;
}

export type SiteSettings = {
  id: string;
  user_created: string | DirectusUser<Schema> | null;
  date_created: "datetime" | null;
  user_updated: string | DirectusUser<Schema> | null;
  date_updated: "datetime" | null;
  site_title: string | null;
  site_description: string | null;
  site_contact_phone: string | null;
  site_contact_email: string | null;
  favicon: string | DirectusFile<Schema> | null;
  site_brand_name: string | null;
  service_area: string | null;
  division_name: string | null;
}

export type CustomDirectusDeployment = {
  webhook_secret: string | null;
}

// GeoJSON Types

export type GeoJSONPoint = {
  type: "Point";
  coordinates: [number, number];
}

export type GeoJSONLineString = {
  type: "LineString";
  coordinates: Array<[number, number]>;
}

export type GeoJSONPolygon = {
  type: "Polygon";
  coordinates: Array<Array<[number, number]>>;
}

export type GeoJSONMultiPoint = {
  type: "MultiPoint";
  coordinates: Array<[number, number]>;
}

export type GeoJSONMultiLineString = {
  type: "MultiLineString";
  coordinates: Array<Array<[number, number]>>;
}

export type GeoJSONMultiPolygon = {
  type: "MultiPolygon";
  coordinates: Array<Array<Array<[number, number]>>>;
}

export type GeoJSONGeometryCollection = {
  type: "GeometryCollection";
  geometries: Array<
    | GeoJSONPoint
    | GeoJSONLineString
    | GeoJSONPolygon
    | GeoJSONMultiPoint
    | GeoJSONMultiLineString
    | GeoJSONMultiPolygon
  >;
}

