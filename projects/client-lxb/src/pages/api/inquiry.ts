import type { APIRoute } from "astro";
import { flattenError } from "zod";
import { createItem, readItems } from "@directus/sdk";
import { dClient } from "@/lib/directus";
import { checkRateLimit } from "@/lib/rate-limit";
import {
  inquirySchema,
  type InquiryPayload,
} from "@/components/inquiry/inquiry-form";

export const prerender = false;

export const POST: APIRoute = async ({ request }) => {
  try {
    const rawData = await request.json();
    const parseResult = inquirySchema.safeParse(rawData);

    if (!parseResult.success) {
      return new Response(
        JSON.stringify({
          error: "Validation failed",
          details: flattenError(parseResult.error).fieldErrors,
        }),
        {
          status: 400,
          headers: { "Content-Type": "application/json" },
        },
      );
    }

    const { data } = parseResult;
    const normalizedEmail = data.email.trim().toLowerCase();

    // 1. In-memory burst protection (prevent rapid-fire double-submits)
    const burst = checkRateLimit(`burst:${normalizedEmail}`, {
      maxRequests: 2,
      windowSeconds: 30,
    });
    if (!burst.allowed) {
      return new Response(
        JSON.stringify({
          error:
            "An inquiry was just received from this email. Please allow a moment before sending another.",
          retryAfter: burst.retryAfter,
        }),
        {
          status: 429,
          headers: { "Content-Type": "application/json" },
        },
      );
    }

    // 2. Persistent database check (max 3 inquiries per email per hour)
    try {
      const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000).toISOString();
      const recent = await dClient.request(
        readItems("inquiry", {
          filter: {
            email: { _eq: normalizedEmail },
            date_created: { _gte: oneHourAgo as any },
          },
          limit: 4,
        }),
      );

      if (recent && recent.length >= 3) {
        return new Response(
          JSON.stringify({
            error:
              "You have already submitted multiple inquiries recently. We have received your details and will get back to you shortly!",
          }),
          {
            status: 429,
            headers: { "Content-Type": "application/json" },
          },
        );
      }
    } catch (checkErr) {
      // Non-blocking: if rate check query fails, continue to create item rather than rejecting legitimate leads
      console.warn("[api/inquiry] Rate-check query notice:", checkErr);
    }

    const payload: InquiryPayload = {
      full_name: data.fullName.trim(),
      email: normalizedEmail,
      phone: data.phone.trim(),
      location_area: data.locationArea.trim(),
      event_date: data.eventDate,
      occasion: data.occasion,
      details: data.details.trim() || null,
      status: "new",
    };

    const result = await dClient.request(createItem("inquiry", payload));

    return new Response(
      JSON.stringify({
        success: true,
        data: result,
      }),
      {
        status: 201,
        headers: { "Content-Type": "application/json" },
      },
    );
  } catch (err) {
    console.error("[api/inquiry] Failed to create inquiry:", err);
    return new Response(
      JSON.stringify({
        error: "Failed to submit inquiry",
        message: err instanceof Error ? err.message : String(err),
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      },
    );
  }
};
