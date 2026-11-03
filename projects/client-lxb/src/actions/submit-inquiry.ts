import { defineAction, ActionError } from "astro:actions";
import { inquirySchema } from "@/components/inquiry-form/schema";
import { checkRateLimit } from "@/lib/rate-limit";

/**
 * Handle public customer inquiry submissions:
 * - Anti-bot honeypot defense
 * - Dual-layer rate limiting (Client IP + Customer Email)
 * - CMS relation resolution (Occasions & Products)
 * - Unique slug generation for routable EmDash collection
 * - Content persistence in EmDash SQLite database
 * - Asynchronous background notification triggering via afterSave hooks
 */
export const submitInquiry = defineAction({
  accept: "json",
  input: inquirySchema,
  handler: async (input, context) => {
    // 1. Anti-Bot Honeypot Trap
    if (input.website_url && input.website_url.trim().length > 0) {
      // Silently discard spam submission with a 200 success response
      return { success: true, inquiryId: "dropped" };
    }

    // 2. Resolve Client IP safely
    let clientIp = "unknown";
    try {
      clientIp = context.clientAddress || "unknown";
    } catch {
      // clientAddress is not supported by Node standalone adapter
    }
    if (clientIp === "unknown" || !clientIp) {
      clientIp = context.request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "unknown";
    }

    // Relaxed rate limits in dev mode for local testing
    const isDev = process.env.NODE_ENV !== "production";

    const ipCheck = checkRateLimit(`ip:${clientIp}`, {
      maxRequests: isDev ? 200 : 5,
      windowSeconds: 600,
    });

    if (!ipCheck.allowed) {
      throw new ActionError({
        code: "TOO_MANY_REQUESTS",
        message: `Too many submissions from your connection. Please wait ${ipCheck.retryAfter ?? 60} seconds before trying again.`,
      });
    }

    // 3. Email Throttling: Max 2 submissions per hour per email address in production
    const normalizedEmail = input.email.toLowerCase().trim();
    const emailCheck = checkRateLimit(`email:${normalizedEmail}`, {
      maxRequests: isDev ? 100 : 2,
      windowSeconds: 3600,
    });

    if (!emailCheck.allowed) {
      throw new ActionError({
        code: "TOO_MANY_REQUESTS",
        message:
          "An inquiry for this email address has already been received recently. Our team will contact you shortly!",
      });
    }

    // 4. EmDash CMS Context
    const emdash = context.locals.emdash;
    if (!emdash) {
      throw new ActionError({
        code: "INTERNAL_SERVER_ERROR",
        message: "CMS service is currently unavailable.",
      });
    }

    // 5. Resolve Relations (Occasion & Products)
    const references: Record<string, string[]> = {};

    try {
      if (input.occasion && emdash.handleContentList) {
        const occRes = await emdash.handleContentList("occasions", { limit: 50 });
        const items = (occRes as any)?.data?.items || (occRes as any)?.items;
        if (Array.isArray(items)) {
          const match = items.find(
            (o: any) =>
              (o.title && o.title.toLowerCase() === input.occasion.toLowerCase()) ||
              (o.slug && o.slug.toLowerCase() === input.occasion.toLowerCase()) ||
              (o.data?.title && o.data.title.toLowerCase() === input.occasion.toLowerCase()),
          );
          if (match?.id) {
            references.occasion = [match.id];
          }
        }
      }

      if (input.selected_products?.length && emdash.handleContentList) {
        const prodRes = await emdash.handleContentList("products", { limit: 50 });
        const items = (prodRes as any)?.data?.items || (prodRes as any)?.items;
        if (Array.isArray(items)) {
          const matchedIds: string[] = [];
          for (const selected of input.selected_products) {
            const match = items.find(
              (p: any) =>
                (p.title && p.title.toLowerCase() === selected.toLowerCase()) ||
                (p.slug && p.slug.toLowerCase() === selected.toLowerCase()) ||
                (p.data?.title && p.data.title.toLowerCase() === selected.toLowerCase()),
            );
            if (match?.id) {
              matchedIds.push(match.id);
            }
          }
          if (matchedIds.length > 0) {
            references.requested_products = matchedIds;
          }
        }
      }
    } catch {
      // Non-critical relation resolution failure; proceed with storage in customer_notes
    }

    // 6. Format Detailed Customer Notes
    const formattedNotes = [
      `Occasion: ${input.occasion}`,
      input.selected_products?.length
        ? `Requested Packages: ${input.selected_products.join(", ")}`
        : null,
      input.palette ? `Color Palette: ${input.palette}` : null,
      `Store Line Care Policy: Accepted & Agreed (${new Date().toLocaleDateString("en-IE")})`,
      "",
      "--- Client Notes & Vision ---",
      input.details?.trim() || "No additional notes provided.",
    ]
      .filter((line) => line !== null)
      .join("\n");

    // 7. Generate a unique slug to satisfy collection publish constraints
    const sanitizedName = input.name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
    const uniqueSlug = `inquiry-${sanitizedName || "client"}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 6)}`;

    // 8. Save to EmDash CMS Database
    const result = await emdash.handleContentCreate("inquiries", {
      slug: uniqueSlug,
      data: {
        customer_name: input.name,
        email: input.email,
        phone: input.phone,
        location: input.location,
        fulfillment_type: input.fulfillment,
        event_date: input.date || null,
        balloon_colors: input.palette || null,
        customer_notes: formattedNotes,
        care_policy_accepted: input.agree_care,
        booking_status: "new_inquiry",
      },
      ...(Object.keys(references).length > 0 ? { references } : {}),
      status: "published",
    });

    if (!result.success) {
      throw new ActionError({
        code: "BAD_REQUEST",
        message: result.error?.message || "Failed to record inquiry in CMS.",
      });
    }

    const createdItem = result.data as { item?: { id?: string } } | undefined;

    return {
      success: true,
      inquiryId: createdItem?.item?.id ?? "unknown",
    };
  },
});
