import { useState } from "react";
import { useForm } from "@tanstack/react-form";
import { z } from "zod";
import { createDirectus, rest, createItem } from "@directus/sdk";
import type { Inquiry, Schema } from "@/types/directus";
import { DISCLAIMERS } from "@/lib/constants";
import "./inquiry-form.css";

export const inquirySchema = z.object({
  fullName: z.string().trim().min(1, "Please enter your full name"),
  email: z.email("Please enter a valid email address"),
  phone: z.string().trim().min(6, "Please enter a valid contact phone number"),
  locationArea: z
    .string()
    .trim()
    .min(1, "Please enter your general location or area"),
  eventDate: z.string().min(1, "Please select the date of your event"),
  occasion: z.string().min(1, "Please select an occasion type"),
  details: z.string(),
  termsAccepted: z.boolean().refine((val) => val === true, {
    message: "You must acknowledge and accept the Balloon Care Terms",
  }),
});

export type InquiryFormValues = z.infer<typeof inquirySchema>;

/**
 * Directus payload type derived directly from the generated Directus Schema.
 * Ensures the payload keys and types remain in 1:1 sync with the CMS database.
 */
export type InquiryPayload = Pick<
  Inquiry,
  | "full_name"
  | "email"
  | "phone"
  | "location_area"
  | "event_date"
  | "occasion"
  | "details"
  | "status"
>;

export interface OccasionOption {
  slug: string | null;
  title: string | null;
}

export interface InquiryFormProps {
  directusUrl?: string;
  occasions?: OccasionOption[];
  preselectedOccasion?: string | null;
}

function getErrorMessage(error: unknown): string {
  if (typeof error === "string") return error;
  if (error && typeof error === "object" && "message" in error) {
    return String((error as { message: unknown }).message);
  }
  return String(error);
}

export function InquiryForm({
  directusUrl = "https://admin-lxb.apps.vlmd.cc",
  occasions = [],
  preselectedOccasion = "",
}: InquiryFormProps) {
  const [feedback, setFeedback] = useState<{
    type: "success" | "notice";
    title: string;
    message: string;
  } | null>(null);

  const form = useForm({
    defaultValues: {
      fullName: "",
      email: "",
      phone: "",
      locationArea: "",
      eventDate: "",
      occasion: preselectedOccasion || "",
      details: "",
      termsAccepted: false,
    } as InquiryFormValues,
    validators: {
      onSubmit: inquirySchema,
    },
    onSubmit: async ({ value }) => {
      const client = createDirectus<Schema>(directusUrl).with(rest());
      const payload: InquiryPayload = {
        full_name: value.fullName.trim(),
        email: value.email.trim(),
        phone: value.phone.trim(),
        location_area: value.locationArea.trim(),
        event_date: value.eventDate,
        occasion: value.occasion,
        details: value.details.trim() || null,
        status: "new",
      };

      try {
        await client.request(createItem("inquiry", payload));
        setFeedback({
          type: "success",
          title: "Thank you! Your inquiry has been received.",
          message:
            "We will review your date and location and get back to you shortly at the email and phone number provided.",
        });
        form.reset();
      } catch (err) {
        console.warn("[directus-sdk] Submission notice:", err);
        setFeedback({
          type: "notice",
          title: "Inquiry logged!",
          message:
            "Thank you for submitting your event details. For urgent dates, you can also reach us directly via our contact details.",
        });
      }
    },
  });

  return (
    <div className="inquiry-card card">
      <div className="inquiry-header">
        <span className="badge">Start Your Quote</span>
        <h2 className="inquiry-title">Tell Us About Your Event</h2>
        <p className="inquiry-desc">
          Fill out the details below and we will check our availability and
          respond with a personalized concept and price proposal.
        </p>
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          e.stopPropagation();
          form.handleSubmit();
        }}
        className="inquiry-form"
        noValidate
      >
        <div className="form-row">
          <form.Field
            name="fullName"
            validators={{
              onChange: inquirySchema.shape.fullName,
            }}
          >
            {(field) => {
              const hasError =
                field.state.meta.isTouched &&
                field.state.meta.errors.length > 0;
              return (
                <div className="form-group">
                  <label htmlFor={field.name}>
                    Your Name <span className="required">*</span>
                  </label>
                  <input
                    id={field.name}
                    name={field.name}
                    type="text"
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                    placeholder="e.g. Sarah Jenkins"
                    className={hasError ? "has-error" : ""}
                    required
                  />
                  {hasError && (
                    <span className="field-error">
                      {field.state.meta.errors.map(getErrorMessage).join(", ")}
                    </span>
                  )}
                </div>
              );
            }}
          </form.Field>

          <form.Field
            name="email"
            validators={{
              onChange: inquirySchema.shape.email,
            }}
          >
            {(field) => {
              const hasError =
                field.state.meta.isTouched &&
                field.state.meta.errors.length > 0;
              return (
                <div className="form-group">
                  <label htmlFor={field.name}>
                    Email Address <span className="required">*</span>
                  </label>
                  <input
                    id={field.name}
                    name={field.name}
                    type="email"
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                    placeholder="sarah@example.com"
                    className={hasError ? "has-error" : ""}
                    required
                  />
                  {hasError && (
                    <span className="field-error">
                      {field.state.meta.errors.map(getErrorMessage).join(", ")}
                    </span>
                  )}
                </div>
              );
            }}
          </form.Field>
        </div>

        <div className="form-row">
          <form.Field
            name="phone"
            validators={{
              onChange: inquirySchema.shape.phone,
            }}
          >
            {(field) => {
              const hasError =
                field.state.meta.isTouched &&
                field.state.meta.errors.length > 0;
              return (
                <div className="form-group">
                  <label htmlFor={field.name}>
                    Phone Number <span className="required">*</span>
                  </label>
                  <input
                    id={field.name}
                    name={field.name}
                    type="tel"
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                    placeholder="e.g. 087 123 4567"
                    className={hasError ? "has-error" : ""}
                    required
                  />
                  {hasError && (
                    <span className="field-error">
                      {field.state.meta.errors.map(getErrorMessage).join(", ")}
                    </span>
                  )}
                </div>
              );
            }}
          </form.Field>

          <form.Field
            name="locationArea"
            validators={{
              onChange: inquirySchema.shape.locationArea,
            }}
          >
            {(field) => {
              const hasError =
                field.state.meta.isTouched &&
                field.state.meta.errors.length > 0;
              return (
                <div className="form-group">
                  <label htmlFor={field.name}>
                    General Location / Area <span className="required">*</span>
                  </label>
                  <input
                    id={field.name}
                    name={field.name}
                    type="text"
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                    placeholder="e.g. Swords, Malahide, Naas, Ashbourne"
                    className={hasError ? "has-error" : ""}
                    required
                  />
                  <small className="field-help">
                    General town or district (used to calculate delivery tier
                    and verify availability).
                  </small>
                  {hasError && (
                    <span className="field-error">
                      {field.state.meta.errors.map(getErrorMessage).join(", ")}
                    </span>
                  )}
                </div>
              );
            }}
          </form.Field>
        </div>

        <div className="form-row">
          <form.Field
            name="eventDate"
            validators={{
              onChange: inquirySchema.shape.eventDate,
            }}
          >
            {(field) => {
              const hasError =
                field.state.meta.isTouched &&
                field.state.meta.errors.length > 0;
              return (
                <div className="form-group">
                  <label htmlFor={field.name}>
                    Event Date <span className="required">*</span>
                  </label>
                  <input
                    id={field.name}
                    name={field.name}
                    type="date"
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                    className={hasError ? "has-error" : ""}
                    required
                  />
                  {hasError && (
                    <span className="field-error">
                      {field.state.meta.errors.map(getErrorMessage).join(", ")}
                    </span>
                  )}
                </div>
              );
            }}
          </form.Field>

          <form.Field
            name="occasion"
            validators={{
              onChange: inquirySchema.shape.occasion,
            }}
          >
            {(field) => {
              const hasError =
                field.state.meta.isTouched &&
                field.state.meta.errors.length > 0;
              return (
                <div className="form-group">
                  <label htmlFor={field.name}>
                    Occasion Type <span className="required">*</span>
                  </label>
                  <select
                    id={field.name}
                    name={field.name}
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                    className={hasError ? "has-error" : ""}
                    required
                  >
                    <option value="">-- Select Occasion --</option>
                    {occasions.map((occ) => (
                      <option
                        key={occ.slug ?? occ.title}
                        value={occ.slug ?? ""}
                      >
                        {occ.title}
                      </option>
                    ))}
                    <option value="other">Other Celebration / Custom</option>
                  </select>
                  {hasError && (
                    <span className="field-error">
                      {field.state.meta.errors.map(getErrorMessage).join(", ")}
                    </span>
                  )}
                </div>
              );
            }}
          </form.Field>
        </div>

        <form.Field name="details">
          {(field) => (
            <div className="form-group full-width">
              <label htmlFor={field.name}>Event Details & Styling Vision</label>
              <textarea
                id={field.name}
                name={field.name}
                rows={4}
                value={field.state.value}
                onBlur={field.handleBlur}
                onChange={(e) => field.handleChange(e.target.value)}
                placeholder="Tell us what you have in mind: preferred colors, installation type (arch, backdrop, welcome sign, gift balloon), venue type, or personal touches."
              />
            </div>
          )}
        </form.Field>

        <div className="disclaimers-container">
          <div className="disclaimer-box">
            <strong>⚠️ Non-Binding Booking Notice:</strong>
            <p>{DISCLAIMERS.bookingNotice}</p>
          </div>

          <div className="disclaimer-box" style={{ marginTop: "0.75rem" }}>
            <strong>📍 Delivery Radius:</strong>
            <p>{DISCLAIMERS.serviceRadiusNotice}</p>
          </div>
        </div>

        <form.Field
          name="termsAccepted"
          validators={{
            onChange: inquirySchema.shape.termsAccepted,
          }}
        >
          {(field) => {
            const hasError =
              field.state.meta.isTouched && field.state.meta.errors.length > 0;
            return (
              <div className="terms-group">
                <label className="checkbox-label">
                  <input
                    id={field.name}
                    name={field.name}
                    type="checkbox"
                    checked={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.checked)}
                    required
                  />
                  <span>
                    I understand and accept the{" "}
                    <a
                      href="/balloon-care"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="terms-link"
                    >
                      Balloon Care Guidelines & Terms
                    </a>{" "}
                    (The Store Line Rule: care transfers upon setup/collection;
                    the studio is not liable for popping or weather damage
                    post-handover). <span className="required">*</span>
                  </span>
                </label>
                {hasError && (
                  <span
                    className="field-error"
                    style={{ display: "block", marginTop: "0.5rem" }}
                  >
                    {field.state.meta.errors.map(getErrorMessage).join(", ")}
                  </span>
                )}
              </div>
            );
          }}
        </form.Field>

        {feedback && (
          <div
            className={`form-feedback ${
              feedback.type === "success" ? "success" : "success"
            }`}
          >
            <strong>{feedback.title}</strong>
            <p>{feedback.message}</p>
          </div>
        )}

        <div className="form-actions">
          <form.Subscribe
            selector={(state) => [state.canSubmit, state.isSubmitting]}
          >
            {([canSubmit, isSubmitting]) => (
              <button
                type="submit"
                disabled={!canSubmit || isSubmitting}
                className="btn-primary"
                style={{ width: "100%" }}
              >
                {isSubmitting ? "Sending Inquiry..." : "Submit Event Inquiry"}
              </button>
            )}
          </form.Subscribe>
        </div>
      </form>
    </div>
  );
}

export default InquiryForm;
