import { z } from "zod";

export const inquirySchema = z.object({
  name: z.string().min(2, "Please enter your full name (at least 2 characters)"),
  phone: z.string().min(6, "Please enter a valid phone number (at least 6 digits)"),
  email: z.string().email("Please enter a valid email address (e.g. name@example.com)"),
  location: z
    .string()
    .min(2, "Please provide your general town or area (e.g. Navan, Ashbourne, Swords)"),
  occasion: z.string().min(1, "Please select an occasion"),
  date: z.string().optional().default(""),
  palette: z.string().optional().default(""),
  fulfillment: z.enum(["delivery", "pickup"]).default("delivery"),
  selected_products: z.array(z.string()).default([]),
  details: z.string().optional().default(""),
  agree_care: z.boolean().refine((val) => val === true, {
    message: "You must acknowledge the Balloon Care & Store Line policy to submit an inquiry",
  }),
});

export type InquiryFormData = z.infer<typeof inquirySchema>;
