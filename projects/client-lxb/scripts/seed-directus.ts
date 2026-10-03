import process from 'node:process';
import {
  createDirectus,
  rest,
  authentication,
  staticToken,
  createCollection,
  createField,
  createItem,
  readCollections,
} from '@directus/sdk';
import {
  DEFAULT_OCCASIONS,
  DEFAULT_PRODUCTS,
  DEFAULT_SEASONAL_BANNER,
} from '../src/lib/constants';

const DIRECTUS_URL =
  process.env.DIRECTUS_URL || 'https://admin-lxb.apps.vlmd.cc';
const ADMIN_TOKEN = process.env.DIRECTUS_ADMIN_TOKEN;
const ADMIN_EMAIL = process.env.DIRECTUS_ADMIN_EMAIL;
const ADMIN_PASSWORD = process.env.DIRECTUS_ADMIN_PASSWORD;

async function getAuthenticatedClient() {
  if (ADMIN_TOKEN) {
    console.log(`Connecting to ${DIRECTUS_URL} using DIRECTUS_ADMIN_TOKEN...`);
    return createDirectus(DIRECTUS_URL)
      .with(rest())
      .with(staticToken(ADMIN_TOKEN));
  }

  if (ADMIN_EMAIL && ADMIN_PASSWORD) {
    console.log(`Connecting to ${DIRECTUS_URL} and authenticating as ${ADMIN_EMAIL}...`);
    const client = createDirectus(DIRECTUS_URL)
      .with(rest())
      .with(authentication());
    await client.login(ADMIN_EMAIL, ADMIN_PASSWORD);
    return client;
  }

  throw new Error(`
Directus admin authentication credentials are required to configure collections.
Please set either:
  1) DIRECTUS_ADMIN_TOKEN="..."
  or
  2) DIRECTUS_ADMIN_EMAIL="..." and DIRECTUS_ADMIN_PASSWORD="..."
in projects/client-lxb/.env or as environment variables.
`);
}

async function runSeed() {
  const client = await getAuthenticatedClient();

  console.log('Checking existing collections on Directus...');
  let existingCollections: string[] = [];
  try {
    const cols = await client.request(readCollections());
    existingCollections = (cols as any[]).map((c) => c.collection);
    console.log('Found existing collections:', existingCollections);
  } catch (err: any) {
    console.error('Failed to list collections:', err?.message || err);
    process.exit(1);
  }

  // 1. Create Occasions Collection
  if (!existingCollections.includes('occasions')) {
    console.log('Creating "occasions" collection...');
    await client.request(
      createCollection({
        collection: 'occasions',
        schema: {},
        meta: {
          icon: 'celebration',
          note: 'Event milestones and celebrations for occasion-first navigation',
        },
      })
    );

    const occasionFields = [
      { field: 'slug', type: 'string', meta: { interface: 'input', required: true, width: 'half' } },
      { field: 'title', type: 'string', meta: { interface: 'input', required: true, width: 'half' } },
      { field: 'subtitle', type: 'string', meta: { interface: 'input', width: 'full' } },
      { field: 'description', type: 'text', meta: { interface: 'input-multiline', width: 'full' } },
      { field: 'badge', type: 'string', meta: { interface: 'input', width: 'half' } },
      { field: 'starting_price', type: 'string', meta: { interface: 'input', width: 'half' } },
      { field: 'highlights', type: 'json', meta: { interface: 'tags', width: 'full' } },
    ];

    for (const f of occasionFields) {
      await client.request(createField('occasions', f as any));
    }
  }

  // 2. Create Products Collection
  if (!existingCollections.includes('products')) {
    console.log('Creating "products" collection...');
    await client.request(
      createCollection({
        collection: 'products',
        schema: {},
        meta: {
          icon: 'inventory_2',
          note: 'Installation types, arches, easels, backdrops and specialty gift balloons',
        },
      })
    );

    const productFields = [
      { field: 'name', type: 'string', meta: { interface: 'input', required: true, width: 'half' } },
      { field: 'subtitle', type: 'string', meta: { interface: 'input', width: 'half' } },
      { field: 'starting_price', type: 'string', meta: { interface: 'input', required: true, width: 'half' } },
      { field: 'description', type: 'text', meta: { interface: 'input-multiline', width: 'full' } },
      { field: 'features', type: 'json', meta: { interface: 'tags', width: 'full' } },
      { field: 'occasion_slugs', type: 'json', meta: { interface: 'tags', width: 'half' } },
      { field: 'is_customizable', type: 'boolean', meta: { interface: 'boolean', width: 'half' } },
    ];

    for (const f of productFields) {
      await client.request(createField('products', f as any));
    }
  }

  // 3. Create Seasonal Banners Collection
  if (!existingCollections.includes('seasonal_banners')) {
    console.log('Creating "seasonal_banners" collection...');
    await client.request(
      createCollection({
        collection: 'seasonal_banners',
        schema: {},
        meta: {
          icon: 'campaign',
          note: 'Dynamic seasonal landing page hero spotlights',
        },
      })
    );

    const bannerFields = [
      { field: 'active_season', type: 'string', meta: { interface: 'input', required: true, width: 'half' } },
      { field: 'headline', type: 'string', meta: { interface: 'input', required: true, width: 'full' } },
      { field: 'subhead', type: 'string', meta: { interface: 'input', width: 'full' } },
      { field: 'cta_text', type: 'string', meta: { interface: 'input', width: 'half' } },
      { field: 'cta_link', type: 'string', meta: { interface: 'input', width: 'half' } },
      { field: 'badge', type: 'string', meta: { interface: 'input', width: 'half' } },
      { field: 'is_active', type: 'boolean', meta: { interface: 'boolean', width: 'half' } },
    ];

    for (const f of bannerFields) {
      await client.request(createField('seasonal_banners', f as any));
    }
  }

  // 4. Create Inquiries Collection
  if (!existingCollections.includes('inquiries')) {
    console.log('Creating "inquiries" collection...');
    await client.request(
      createCollection({
        collection: 'inquiries',
        schema: {},
        meta: {
          icon: 'mail',
          note: 'Event booking requests submitted from the web inquiry form',
        },
      })
    );

    const inquiryFields = [
      { field: 'full_name', type: 'string', meta: { interface: 'input', required: true, width: 'half' } },
      { field: 'email', type: 'string', meta: { interface: 'input', required: true, width: 'half' } },
      { field: 'phone', type: 'string', meta: { interface: 'input', required: true, width: 'half' } },
      { field: 'location_area', type: 'string', meta: { interface: 'input', required: true, width: 'half' } },
      { field: 'event_date', type: 'string', meta: { interface: 'input', required: true, width: 'half' } },
      { field: 'occasion', type: 'string', meta: { interface: 'input', required: true, width: 'half' } },
      { field: 'details', type: 'text', meta: { interface: 'input-multiline', width: 'full' } },
      { field: 'terms_accepted', type: 'boolean', meta: { interface: 'boolean', width: 'half' } },
      { field: 'status', type: 'string', meta: { interface: 'select-dropdown', width: 'half' } },
    ];

    for (const f of inquiryFields) {
      await client.request(createField('inquiries', f as any));
    }
  }

  // 5. Seed Initial Data
  console.log('Seeding initial occasions...');
  for (const occ of DEFAULT_OCCASIONS) {
    try {
      await client.request(createItem('occasions', occ as any));
      console.log(`  ✓ Seeded occasion: ${occ.title}`);
    } catch {
      console.log(`  - Occasion ${occ.slug} already exists or was skipped`);
    }
  }

  console.log('Seeding initial products...');
  for (const prod of DEFAULT_PRODUCTS) {
    try {
      await client.request(createItem('products', prod as any));
      console.log(`  ✓ Seeded product: ${prod.name}`);
    } catch {
      console.log(`  - Product ${prod.name} already exists or was skipped`);
    }
  }

  console.log('Seeding initial seasonal banner...');
  try {
    await client.request(createItem('seasonal_banners', DEFAULT_SEASONAL_BANNER as any));
    console.log(`  ✓ Seeded banner: ${DEFAULT_SEASONAL_BANNER.headline}`);
  } catch {
    console.log('  - Seasonal banner already exists or was skipped');
  }

  console.log(`
🎉 Directus schema creation and seeding complete!
Next step: In your Directus admin panel (Settings > Roles & Permissions > Public):
  - Grant Public Read access to: occasions, products, seasonal_banners
  - Grant Public Create access to: inquiries
`);
}

runSeed().catch((err) => {
  console.error('Fatal seed error:', err);
  process.exit(1);
});
