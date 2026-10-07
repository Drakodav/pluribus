import type { APIRoute } from "astro";
import { flattenError } from "zod";
import { createItem } from "@directus/sdk";
import { dClient } from "@/lib/directus";
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
    const payload: InquiryPayload = {
      full_name: data.fullName.trim(),
      email: data.email.trim(),
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
