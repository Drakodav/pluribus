import { definePlugin, type ContentHookEvent, type PluginContext } from "emdash";

export interface InquiryNotifierOptions {
  /** Single admin email or list of admin emails (can also be configured via EmDash Admin Settings) */
  adminEmails?: string | string[];
  /** Backwards compatibility alias for single admin email */
  studioEmail?: string;
  /** Display sender name for email headers */
  senderName?: string;
  /** Whether to dispatch auto-receipt to the customer */
  enableCustomerConfirmation?: boolean;
}

const SETTINGS_SCHEMA = {
  adminEmails: {
    type: "string" as const,
    label: "Admin Notification Email(s)",
    description:
      "Comma-separated or newline-separated email addresses to notify when a new inquiry arrives (e.g. vmedves@gmail.com, bookings@luxebear.ie).",
    default: "vmedves@gmail.com",
  },
  enableCustomerConfirmation: {
    type: "boolean" as const,
    label: "Send Customer Confirmation Email",
    description:
      "Automatically send an acknowledgment receipt and The Store Line Balloon Care Policy to the customer.",
    default: true,
  },
  senderDisplayName: {
    type: "string" as const,
    label: "Sender Display Name",
    description: "Brand display name used on notification emails.",
    default: "Luxe Bear Balloon Bar",
  },
};

export function createPlugin(options: InquiryNotifierOptions = {}) {
  return definePlugin({
    id: "lxb-inquiry-notifier",
    version: "1.0.0",
    capabilities: ["content:read", "email:send"],
    admin: {
      settingsSchema: SETTINGS_SCHEMA,
    },
    hooks: {
      "content:afterSave": async (event: ContentHookEvent, ctx: PluginContext) => {
        // Only trigger on newly created inquiries
        if (event.collection !== "inquiries" || !event.isNew) {
          return;
        }

        const data = (event.content?.data as Record<string, any>) || event.content || {};
        const customerName = data.customer_name || "New Client";
        const customerEmail = data.email;
        const customerPhone = data.phone || "Not provided";
        const location = data.location || "Not specified";
        const occasion = data.occasion || "Celebration";
        const eventDate = data.event_date || "Date to be confirmed";
        const palette = data.balloon_colors || "Studio recommendation / TBD";
        const fulfillment =
          data.fulfillment_type === "pickup"
            ? "Customer Collection / Pickup"
            : "Delivery & On-Site Setup";
        const notes = data.customer_notes || "None provided";
        const products = Array.isArray(data.requested_products)
          ? data.requested_products.join(", ")
          : data.requested_products || "Signature styling";

        if (!ctx.email) {
          ctx.log.warn(
            "Email service is not available or no provider configured in EmDash settings.",
          );
          return;
        }

        // 1. Resolve Admin Settings & Storage
        let configuredAdminEmails: string | null = null;
        let enableCustomerConfirmation = options.enableCustomerConfirmation ?? true;
        let senderDisplayName = options.senderName || "Luxe Bear Balloon Bar";

        try {
          if (ctx.settings) {
            configuredAdminEmails = await ctx.settings.get<string>("adminEmails");
            const customerSetting = await ctx.settings.get<boolean>("enableCustomerConfirmation");
            if (typeof customerSetting === "boolean") {
              enableCustomerConfirmation = customerSetting;
            }
            const senderSetting = await ctx.settings.get<string>("senderDisplayName");
            if (senderSetting) {
              senderDisplayName = senderSetting;
            }
          }
        } catch (settingsErr: any) {
          ctx.log.warn(
            `[inquiry-notifier] Could not read settings from store, falling back to defaults: ${settingsErr.message}`,
          );
        }

        // Resolve recipients list from: Settings -> Options (array or string) -> StudioEmail -> Env -> Default
        const rawRecipients =
          configuredAdminEmails ||
          (Array.isArray(options.adminEmails)
            ? options.adminEmails.join(",")
            : options.adminEmails) ||
          options.studioEmail ||
          process.env.INQUIRY_NOTIFICATION_EMAIL ||
          "vmedves@gmail.com";

        const adminRecipients = rawRecipients
          .split(/[,;\n\r\t]+/)
          .map((e) => e.trim())
          .filter((e) => e.length > 0 && e.includes("@"));

        if (adminRecipients.length === 0) {
          adminRecipients.push("vmedves@gmail.com");
        }

        const [primaryAdmin, ...ccAdmins] = adminRecipients;

        // 2. Dispatch Studio Owner / Admin Notification Email
        try {
          await ctx.email.send({
            to: primaryAdmin,
            cc: ccAdmins.length > 0 ? ccAdmins : undefined,
            replyTo: customerEmail || undefined,
            subject: `🎈 New Booking Inquiry: ${customerName} — ${occasion} (${eventDate})`,
            text: `
New Booking Inquiry from ${senderDisplayName}:

Client: ${customerName}
Email: ${customerEmail}
Phone: ${customerPhone}
Location / Town: ${location}
Fulfillment: ${fulfillment}
Occasion: ${occasion}
Date: ${eventDate}
Preferred Palette: ${palette}
Packages of Interest: ${products}

Client Notes:
${notes}

Inquiry ID: ${event.content?.id || "N/A"}
View in Admin: ${ctx.url("/_emdash/admin")}
            `.trim(),
            html: `
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; color: #231c18; background-color: #faf8f5; border-radius: 16px;">
  <div style="text-align: center; margin-bottom: 24px;">
    <span style="font-size: 32px;">🎈</span>
    <h1 style="font-size: 24px; font-weight: 800; color: #231c18; margin: 8px 0 4px;">New Booking Inquiry</h1>
    <p style="font-size: 14px; color: #a8783d; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin: 0;">${senderDisplayName}</p>
  </div>

  <div style="background-color: #ffffff; border: 1px solid #edd8b4; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
    <h2 style="font-size: 16px; font-weight: 700; border-bottom: 1px solid #f5ebe7; padding-bottom: 8px; margin-top: 0;">Customer Information</h2>
    <p style="margin: 6px 0; font-size: 14px;"><strong>Name:</strong> ${customerName}</p>
    <p style="margin: 6px 0; font-size: 14px;"><strong>Email:</strong> <a href="mailto:${customerEmail}" style="color: #a8783d;">${customerEmail}</a></p>
    <p style="margin: 6px 0; font-size: 14px;"><strong>Phone:</strong> <a href="tel:${customerPhone}" style="color: #a8783d;">${customerPhone}</a></p>
    <p style="margin: 6px 0; font-size: 14px;"><strong>Location / Town:</strong> ${location}</p>
    <p style="margin: 6px 0; font-size: 14px;"><strong>Fulfillment:</strong> ${fulfillment}</p>
  </div>

  <div style="background-color: #ffffff; border: 1px solid #edd8b4; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
    <h2 style="font-size: 16px; font-weight: 700; border-bottom: 1px solid #f5ebe7; padding-bottom: 8px; margin-top: 0;">Celebration Details</h2>
    <p style="margin: 6px 0; font-size: 14px;"><strong>Occasion:</strong> ${occasion}</p>
    <p style="margin: 6px 0; font-size: 14px;"><strong>Event Date:</strong> ${eventDate}</p>
    <p style="margin: 6px 0; font-size: 14px;"><strong>Color Palette:</strong> ${palette}</p>
    <p style="margin: 6px 0; font-size: 14px;"><strong>Packages / Offerings:</strong> ${products}</p>
    <div style="margin-top: 12px; padding-top: 10px; border-top: 1px dashed #e5e7eb;">
      <strong style="font-size: 14px;">Client Vision / Custom Notes:</strong>
      <p style="margin: 6px 0 0; font-size: 14px; color: #4b5563; white-space: pre-wrap;">${notes}</p>
    </div>
  </div>

  <div style="text-align: center; margin-top: 24px;">
    <a href="${ctx.url("/_emdash/admin")}" style="display: inline-block; background-color: #a8783d; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 9999px; font-weight: 600; font-size: 14px;">
      Open in EmDash Admin &rarr;
    </a>
  </div>
</div>
            `.trim(),
          });
          ctx.log.info(
            `[inquiry-notifier] Studio notification sent to ${adminRecipients.join(", ")} for inquiry from ${customerName}`,
          );
        } catch (err: any) {
          ctx.log.error(`[inquiry-notifier] Failed to send studio alert: ${err.message}`);
        }

        // 3. Customer Confirmation Receipt & Care Policy
        if (enableCustomerConfirmation && customerEmail) {
          try {
            await ctx.email.send({
              to: customerEmail,
              replyTo: primaryAdmin,
              subject: `We've received your booking inquiry! — ${senderDisplayName}`,
              text: `
Hi ${customerName},

Thank you for reaching out to ${senderDisplayName}!

We have received your celebration inquiry for your ${occasion} (${eventDate}).

Our team is currently reviewing our calendar and setup availability for ${location}. We will reach out shortly via email or phone to discuss your color palette, bespoke package options, and exact pricing.

⚠️ Booking Notice:
Submitting an inquiry does not guarantee or confirm your booking until date availability is confirmed by our studio.

🎈 Balloon Care & The Store Line Policy:
Balloons are delicate and sensitive to temperature, sunlight, and sharp hazards. Once delivered, installed, or collected, care responsibility belongs to the client.

Warm regards,
${senderDisplayName}
              `.trim(),
              html: `
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; color: #231c18; background-color: #faf8f5; border-radius: 16px;">
  <div style="text-align: center; margin-bottom: 24px;">
    <span style="font-size: 32px;">🎈</span>
    <h1 style="font-size: 24px; font-weight: 800; color: #231c18; margin: 8px 0 4px;">Thank You, ${customerName}!</h1>
    <p style="font-size: 14px; color: #a8783d; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin: 0;">${senderDisplayName}</p>
  </div>

  <div style="background-color: #ffffff; border: 1px solid #edd8b4; border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
    <p style="font-size: 15px; line-height: 1.6; margin-top: 0;">
      We have received your booking inquiry for your upcoming <strong>${occasion}</strong>${eventDate ? ` on <strong>${eventDate}</strong>` : ""}.
    </p>
    <p style="font-size: 15px; line-height: 1.6; color: #4b5563;">
      Our styling team is checking date and setup availability for your area (<strong>${location}</strong>). We will be in touch shortly to finalize custom details and provide exact pricing.
    </p>

    <div style="margin: 20px 0; padding: 16px; background-color: #faf8f5; border-radius: 8px; border-left: 4px solid #a8783d;">
      <h3 style="margin: 0 0 8px; font-size: 14px; font-weight: 700; color: #231c18;">⚠️ Booking Confirmation Notice</h3>
      <p style="margin: 0; font-size: 13px; color: #6b7280; line-height: 1.5;">
        Submitting this inquiry does not guarantee or secure your reservation. Our studio owner will review availability and confirm your booking.
      </p>
    </div>

    <div style="margin: 20px 0 0; padding: 16px; background-color: #faf8f5; border-radius: 8px; border-left: 4px solid #d48a7f;">
      <h3 style="margin: 0 0 8px; font-size: 14px; font-weight: 700; color: #231c18;">🎈 Balloon Care & The Store Line Policy</h3>
      <p style="margin: 0; font-size: 13px; color: #6b7280; line-height: 1.5;">
        Balloons are sensitive living art. Keep them away from direct sunlight, hot vehicles, and sharp edges. Once installed or collected, care transfers to the client.
      </p>
    </div>
  </div>

  <div style="text-align: center; color: #8c786a; font-size: 12px; margin-top: 24px;">
    <p style="margin: 0;">© ${new Date().getFullYear()} ${senderDisplayName}. All rights reserved.</p>
  </div>
</div>
              `.trim(),
            });
            ctx.log.info(`[inquiry-notifier] Confirmation receipt sent to ${customerEmail}`);
          } catch (err: any) {
            ctx.log.error(`[inquiry-notifier] Failed to send customer receipt: ${err.message}`);
          }
        }
      },
    },
  });
}

export function inquiryNotifierPlugin(options: InquiryNotifierOptions = {}) {
  return {
    id: "lxb-inquiry-notifier",
    version: "1.0.0",
    format: "native" as const,
    entrypoint: pathToFileURL(),
    options,
    capabilities: ["content:read", "email:send"],
    settingsSchema: SETTINGS_SCHEMA,
  };
}

function pathToFileURL() {
  return new URL("./inquiry-notifier.ts", import.meta.url).pathname;
}

export default inquiryNotifierPlugin;
