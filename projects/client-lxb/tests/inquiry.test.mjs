import test from "node:test";
import assert from "node:assert/strict";
import { DatabaseSync } from "node:sqlite";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { inquirySchema } from "../src/components/inquiry-form/schema.ts";
import { checkRateLimit } from "../src/lib/rate-limit.ts";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dbPath = path.resolve(__dirname, "../.emdash/data/data.db");

// Helper to format ISO date
function getRelativeIsoDate(daysOffset = 0) {
  const d = new Date();
  d.setDate(d.getDate() + daysOffset);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

test("Inquiry Schema — Valid submissions", async (t) => {
  await t.test("Valid full payload passes parsing", () => {
    const payload = {
      name: "Eleanor Vance",
      phone: "0871234567",
      email: "eleanor@example.com",
      location: "Ashbourne, Co. Meath",
      occasion: "Birthdays",
      date: getRelativeIsoDate(14), // 2 weeks in future
      palette: "Champagne Luxe & Blush",
      fulfillment: "delivery",
      selected_products: ["The Signature Bear Balloon Bouquet"],
      details: "Please include gold foil lettering 'Happy 30th'.",
      agree_care: true,
      website_url: "",
    };

    const res = inquirySchema.safeParse(payload);
    assert.equal(res.success, true);
    if (res.success) {
      assert.equal(res.data.name, "Eleanor Vance");
      assert.equal(res.data.agree_care, true);
    }
  });

  await t.test("Valid minimal payload with empty optionals passes parsing", () => {
    const payload = {
      name: "Mark O'Connor",
      phone: "0859876543",
      email: "mark@example.com",
      location: "Navan",
      occasion: "Gender Reveals",
      date: "",
      palette: "",
      fulfillment: "pickup",
      selected_products: [],
      details: "",
      agree_care: true,
      website_url: "",
    };

    const res = inquirySchema.safeParse(payload);
    assert.equal(res.success, true);
    if (res.success) {
      assert.equal(res.data.fulfillment, "pickup");
      assert.deepEqual(res.data.selected_products, []);
    }
  });

  await t.test("Today's date is allowed", () => {
    const payload = {
      name: "Sarah Miller",
      phone: "0831112222",
      email: "sarah@example.com",
      location: "Swords",
      occasion: "Pop-Me Gifts",
      date: getRelativeIsoDate(0), // Today
      fulfillment: "delivery",
      selected_products: [],
      agree_care: true,
      website_url: "",
    };

    const res = inquirySchema.safeParse(payload);
    assert.equal(res.success, true);
  });
});

test("Inquiry Schema — Validation Rules & Edge Cases", async (t) => {
  await t.test("Rejects past date with custom message", () => {
    const payload = {
      name: "Sarah Miller",
      phone: "0831112222",
      email: "sarah@example.com",
      location: "Swords",
      occasion: "Pop-Me Gifts",
      date: getRelativeIsoDate(-5), // 5 days in past!
      fulfillment: "delivery",
      agree_care: true,
      website_url: "",
    };

    const res = inquirySchema.safeParse(payload);
    assert.equal(res.success, false);
    if (!res.success) {
      const dateIssue = res.error.issues.find((i) => i.path.includes("date"));
      assert.ok(dateIssue, "Expected date issue");
      assert.equal(dateIssue.message, "Event date cannot be in the past");
    }
  });

  await t.test("Rejects unacknowledged care policy (agree_care: false)", () => {
    const payload = {
      name: "David Smith",
      phone: "0876543210",
      email: "david@example.com",
      location: "Ratoath",
      occasion: "Birthdays",
      agree_care: false, // Refused
      website_url: "",
    };

    const res = inquirySchema.safeParse(payload);
    assert.equal(res.success, false);
    if (!res.success) {
      const careIssue = res.error.issues.find((i) => i.path.includes("agree_care"));
      assert.ok(careIssue, "Expected care policy issue");
      assert.match(careIssue.message, /acknowledge the Balloon Care/);
    }
  });

  await t.test("Rejects invalid email format", () => {
    const payload = {
      name: "David Smith",
      phone: "0876543210",
      email: "not-an-email",
      location: "Ratoath",
      occasion: "Birthdays",
      agree_care: true,
    };

    const res = inquirySchema.safeParse(payload);
    assert.equal(res.success, false);
    if (!res.success) {
      const emailIssue = res.error.issues.find((i) => i.path.includes("email"));
      assert.ok(emailIssue, "Expected email issue");
    }
  });

  await t.test("Rejects too-short name (< 2 characters)", () => {
    const payload = {
      name: "D",
      phone: "0876543210",
      email: "david@example.com",
      location: "Ratoath",
      occasion: "Birthdays",
      agree_care: true,
    };

    const res = inquirySchema.safeParse(payload);
    assert.equal(res.success, false);
  });

  await t.test("Rejects too-short phone (< 6 digits)", () => {
    const payload = {
      name: "David Smith",
      phone: "123",
      email: "david@example.com",
      location: "Ratoath",
      occasion: "Birthdays",
      agree_care: true,
    };

    const res = inquirySchema.safeParse(payload);
    assert.equal(res.success, false);
  });
});

test("Rate Limiter — Window & Throttling", () => {
  const testKey = `test-client-${Date.now()}`;

  // First 3 requests should be allowed
  const r1 = checkRateLimit(testKey, { maxRequests: 3, windowSeconds: 2 });
  assert.equal(r1.allowed, true);
  assert.equal(r1.remaining, 2);

  const r2 = checkRateLimit(testKey, { maxRequests: 3, windowSeconds: 2 });
  assert.equal(r2.allowed, true);
  assert.equal(r2.remaining, 1);

  const r3 = checkRateLimit(testKey, { maxRequests: 3, windowSeconds: 2 });
  assert.equal(r3.allowed, true);
  assert.equal(r3.remaining, 0);

  // 4th request must be blocked
  const r4 = checkRateLimit(testKey, { maxRequests: 3, windowSeconds: 2 });
  assert.equal(r4.allowed, false);
  assert.ok(r4.retryAfter !== undefined && r4.retryAfter > 0);
});

test("Database Schema & Column Integrity — ec_inquiries", () => {
  const db = new DatabaseSync(dbPath);

  // Verify table columns
  const columns = db.prepare("PRAGMA table_info(ec_inquiries)").all();
  const colNames = new Set(columns.map((c) => c.name));

  assert.ok(colNames.has("customer_name"), "Missing customer_name");
  assert.ok(colNames.has("email"), "Missing email");
  assert.ok(colNames.has("phone"), "Missing phone");
  assert.ok(colNames.has("location"), "Missing location");
  assert.ok(colNames.has("fulfillment_type"), "Missing fulfillment_type");
  assert.ok(colNames.has("event_date"), "Missing event_date");
  assert.ok(colNames.has("balloon_colors"), "Missing balloon_colors");
  assert.ok(colNames.has("customer_notes"), "Missing customer_notes");
  assert.ok(colNames.has("care_policy_accepted"), "Missing care_policy_accepted column");
  assert.ok(colNames.has("booking_status"), "Missing booking_status");

  // Verify field registry in _emdash_fields
  const fieldRow = db
    .prepare("SELECT slug, type, required FROM _emdash_fields WHERE slug = 'care_policy_accepted'")
    .get();
  assert.ok(fieldRow, "Missing care_policy_accepted in _emdash_fields");
  assert.equal(fieldRow.slug, "care_policy_accepted");
  assert.equal(fieldRow.type, "boolean");

  // Verify collection configuration in _emdash_collections
  const colRow = db
    .prepare("SELECT slug, title_field FROM _emdash_collections WHERE slug = 'inquiries'")
    .get();
  assert.ok(colRow, "Missing inquiries in _emdash_collections");
  assert.equal(colRow.title_field, "customer_name");

  db.close();
});

test("End-to-End Inquiry Persistence in Database", () => {
  const db = new DatabaseSync(dbPath);

  const testId = `test-inq-${Date.now()}`;
  const testSlug = `inquiry-test-customer-${Date.now().toString(36)}`;

  // Test simulated insert
  const stmt = db.prepare(`
    INSERT INTO ec_inquiries (
      id, slug, status, customer_name, email, phone, location,
      fulfillment_type, event_date, balloon_colors, customer_notes,
      care_policy_accepted, booking_status
    ) VALUES (
      ?, ?, 'published', ?, ?, ?, ?,
      ?, ?, ?, ?,
      ?, 'new_inquiry'
    )
  `);

  stmt.run(
    testId,
    testSlug,
    "Sophia Loren",
    "sophia@example.com",
    "0879998888",
    "Dunboyne",
    "delivery",
    "2026-11-20",
    "Champagne & Pearl White",
    "Store Line Care Policy: Accepted & Agreed\nClient Notes: Balloon garland over entrance.",
    1, // care_policy_accepted
  );

  // Read back and assert
  const inserted = db.prepare("SELECT * FROM ec_inquiries WHERE id = ?").get(testId);
  assert.ok(inserted, "Inserted inquiry was not found in database");
  assert.equal(inserted.customer_name, "Sophia Loren");
  assert.equal(inserted.email, "sophia@example.com");
  assert.equal(inserted.location, "Dunboyne");
  assert.equal(inserted.care_policy_accepted, 1);
  assert.equal(inserted.booking_status, "new_inquiry");
  assert.equal(inserted.status, "published");
  assert.equal(inserted.slug, testSlug);

  // Clean up
  db.prepare("DELETE FROM ec_inquiries WHERE id = ?").run(testId);
  const verifyDeleted = db.prepare("SELECT * FROM ec_inquiries WHERE id = ?").get(testId);
  assert.equal(verifyDeleted, undefined);

  db.close();
});
