import type { Occasion, Product, SeasonalBanner } from '../types/directus';

export const SITE_METADATA = {
  title: 'Luxe Bear - Balloon Bar | Luxury Balloon Styling & Event Decor',
  description:
    'Bespoke luxury balloon styling, organic arches, backdrops, and specialty pop-me balloons for milestone birthdays, communions, confirmations, gender reveals, and bridal celebrations.',
  brandName: 'Luxe Bear Studio',
  divisionName: 'Balloon Bar',
  alias: 'LXB',
  contactPhone: '+353 00 000 0000',
  contactEmail: 'hello@luxebear.ie',
  defaultServiceArea: 'Dublin, Meath, Kildare & surrounding Leinster areas',
};

export const DEFAULT_OCCASIONS: Occasion[] = [
  {
    slug: 'birthdays',
    title: 'Milestone & Birthday Celebrations',
    subtitle: 'From whimsical 1st birthdays to luxury milestone 21st, 30th & 50th setups.',
    description:
      'Make your milestone unforgettable with organic balloon arches, marquee number frames, personalized backdrop signage, and bespoke color palettes tailored to your theme.',
    badge: 'Popular',
    starting_price: 'From €120',
    highlights: ['Giant Number Frames', 'Organic Demi-Arches', 'Custom Vinyl Name Backdrops'],
  },
  {
    slug: 'communions-confirmations',
    title: 'Communions, Christenings & Confirmations',
    subtitle: 'Elegant, timeless decor for sacred family milestones.',
    description:
      'Soft whites, golds, champagne, and muted eucalyptus tones designed around easels, personalized welcome plaques, and church/home party backdrops.',
    badge: 'Spring Season',
    starting_price: 'From €140',
    highlights: ['Easel Welcome Signs with Clusters', 'Half Arch on Circular Backdrops', 'Personalized Holy Communion Signs'],
  },
  {
    slug: 'gender-reveals',
    title: 'Gender Reveals & Baby Showers',
    subtitle: 'High-anticipation reveals with signature pop-me balloons & pastel garlands.',
    description:
      'Featuring our proprietary dual-layer bubble pop balloon — where the inner latex explodes into pink or blue while the outer clear bubble stays intact — plus dreamy cloud garland backdrops.',
    badge: 'Signature',
    starting_price: 'From €85',
    highlights: ['Dual-Layer Bubble Pop Balloon', 'Baby Shower Balloon Easels', 'Boy or Girl Mini Clusters'],
  },
  {
    slug: 'bridal',
    title: 'Bridal Era & Weddings',
    subtitle: 'Sophisticated aesthetics for hen parties, bridal suites, and receptions.',
    description:
      'Chic pearlescent tones, crisp ivories, and champagne palettes. Perfect for bridal shower photo zones, bachelorette party hotel installations, and ceremony entrance easels.',
    badge: 'Trending',
    starting_price: 'From €150',
    highlights: ['Bride-to-Be Shimmer Backdrops', 'Champagne Bottle Cloud Installations', 'Custom Vinyl Surname Accents'],
  },
  {
    slug: 'gifts',
    title: 'Pop-Me Gifts & Stuffed Balloons',
    subtitle: 'Surprise gifts suspended inside clear luxury balloons.',
    description:
      'Bring your own special gift (perfume, baby wear, jewelry, plush toys) and we expertly encase it inside a luxury helium or air-filled clear bubble balloon adorned with ribbon and mini latex accents.',
    badge: 'Bespoke Gifts',
    starting_price: 'From €50',
    highlights: ['Customer-Supplied Gift Stuffing', 'Pop-Me Pin Included', 'Personalized Calligraphy Vinyl'],
  },
];

export const DEFAULT_PRODUCTS: Product[] = [
  {
    id: 'prod-organic-arch',
    name: 'Organic Balloon Arch',
    subtitle: 'Full freeform organic installation',
    starting_price: '€180',
    description:
      'A luxury organic balloon garland using 5" to 24" premium biodegradable latex balloons. Can be wall-mounted, free-standing, or woven around architectural fixtures.',
    features: ['Custom 3-color palette', 'Matte, reflex, and pearl finishes available', 'Professional on-site installation'],
    occasion_slugs: ['birthdays', 'communions-confirmations', 'bridal'],
  },
  {
    id: 'prod-welcome-sign-arch',
    name: 'Welcome Sign & Easel Installation',
    subtitle: 'Acrylic or wooden welcome plaque with organic cluster',
    starting_price: '€120',
    description:
      'High-grade acrylic or wooden easel welcome sign with customized vinyl lettering. Available standalone or framed by an organic cascading balloon garland.',
    features: ['Easel hire included', 'Custom vinyl lettering', 'Optional floral or greenery accents'],
    occasion_slugs: ['communions-confirmations', 'birthdays', 'bridal', 'gender-reveals'],
    is_customizable: true,
  },
  {
    id: 'prod-half-arch-backdrop',
    name: 'Half Arch & Backdrop Set',
    subtitle: 'Statement photo zone backdrop with organic demi-arch',
    starting_price: '€220',
    description:
      'A solid arch, sailboard, or hoop backdrop paired with an organic half arch. Includes customizable vinyl decals (e.g. "Happy 30th Sarah" or "First Holy Communion").',
    features: ['Backdrop panel rental included', 'Customized vinyl typography', 'Full teardown options'],
    occasion_slugs: ['birthdays', 'communions-confirmations', 'bridal'],
    is_customizable: true,
  },
  {
    id: 'prod-dual-layer-reveal',
    name: 'Dual-Layer Bubble Gender Reveal',
    subtitle: 'Our signature zero-mess outer bubble reveal',
    starting_price: '€85',
    description:
      'A crystal-clear outer bubble holding an opaque black or colored latex balloon stuffed with pink or blue confetti. When popped with the supplied pin, the inner latex bursts while the outer bubble stays intact, giving a breathtaking, safe reveal.',
    features: ['Supplied popping pin with ribbon', 'Gender envelope handover option', 'Weighted ribbon base'],
    occasion_slugs: ['gender-reveals'],
  },
  {
    id: 'prod-pop-me-gift',
    name: 'Pop-Me Stuffed Gift Balloon',
    subtitle: 'Encapsulated personalized gift packaging',
    starting_price: '€55',
    description:
      'A luxury clear sphere balloon stuffed with gifts provided by you (soft toys, small gifts, clothing, gift cards). Finished with satin ribbon, mini balloons, and a popping pin.',
    features: ['Customer provides gift (subject to size limits)', 'Includes popping pin', 'Personalized recipient name'],
    occasion_slugs: ['gifts', 'birthdays'],
  },
];

export const DEFAULT_SEASONAL_BANNER: SeasonalBanner = {
  id: 'banner-winter-holiday',
  active_season: 'Christmas & Holiday Celebrations',
  headline: 'Transform Your Holiday Celebration with Luxe Balloons',
  subhead: 'From intimate festive family dinners to dazzling New Year’s Eve photo zones.',
  cta_text: 'Inquire for Holiday Dates',
  cta_link: '/book',
  badge: 'Holiday Booking Open',
  is_active: true,
};

export const DISCLAIMERS = {
  bookingNotice:
    'Please note: Submitting this form is an inquiry only and DOES NOT confirm your booking. We will verify our date availability and reach out to you directly with a tailored quote and deposit details.',
  serviceRadiusNotice:
    'We proudly serve Dublin, Meath, Kildare, and surrounding Leinster regions. Inquiries outside our primary service radius are welcome and subject to a reasonable travel/delivery tier surcharge.',
  balloonCareHandoff:
    'The Store Line Rule: Once balloon installations are set up or collected, care and environmental responsibility transfer to the client. Balloons are sensitive to sunlight, heat, sharp objects, and pets. Luxe Bear Studio is not liable for popping or damage occurring after handover.',
};
