import { z } from "zod";

export const inquirySchema = z.object({
  name: z.string().min(2, "Please enter your full name (at least 2 characters)"),
  phone: z.string().min(6, "Please enter a valid phone number (at least 6 digits)"),
  email: z.email("Please enter a valid email address (e.g. name@example.com)"),
  location: z
    .string()
    .min(2, "Please provide your general town or area (e.g. Navan, Ashbourne, Swords)"),
  occasion: z.string().min(1, "Please select an occasion"),
  date: z
    .string()
    .optional()
    .default("")
    .refine(
      (val) => {
        if (!val || val.trim().length === 0) return true;
        const parts = val.split("-");
        if (parts.length !== 3) return true;
        const d = new Date(
          parseInt(parts[0], 10),
          parseInt(parts[1], 10) - 1,
          parseInt(parts[2], 10),
        );
        if (isNaN(d.getTime())) return false;
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        return d >= today;
      },
      { message: "Event date cannot be in the past" },
    ),
  palette: z.string().optional().default(""),
  fulfillment: z.enum(["delivery", "pickup"]).default("delivery"),
  selected_products: z.array(z.string()).default([]),
  details: z.string().optional().default(""),
  agree_care: z.boolean().refine((val) => val === true, {
    message: "You must acknowledge the Balloon Care & Store Line policy to submit an inquiry",
  }),
  /** Honeypot anti-bot trap (must be empty) */
  website_url: z.string().optional().default(""),
});

export type InquiryFormData = z.infer<typeof inquirySchema>;
