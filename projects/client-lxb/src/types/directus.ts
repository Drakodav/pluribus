export interface Occasion {
  id?: string | number;
  slug: string;
  title: string;
  subtitle: string;
  description: string;
  hero_image?: string;
  badge?: string;
  starting_price?: string;
  highlights?: string[];
}

export interface Product {
  id?: string | number;
  name: string;
  subtitle?: string;
  starting_price: string;
  description: string;
  features?: string[];
  image?: string;
  occasion_slugs?: string[];
  is_customizable?: boolean;
}

export interface SeasonalBanner {
  id?: string | number;
  active_season: string;
  headline: string;
  subhead: string;
  cta_text: string;
  cta_link: string;
  badge?: string;
  is_active: boolean;
}

export interface Inquiry {
  id?: string | number;
  full_name: string;
  email: string;
  phone: string;
  location_area: string;
  event_date: string;
  occasion: string;
  details: string;
  terms_accepted: boolean;
  status?: 'new' | 'contacted' | 'booked' | 'archived';
  date_created?: string;
}

export interface DirectusSchema {
  occasions: Occasion[];
  products: Product[];
  seasonal_banners: SeasonalBanner[];
  inquiries: Inquiry[];
}
