import * as React from "react";
import { useForm } from "@tanstack/react-form";
import { actions } from "astro:actions";
import { inquirySchema, type InquiryFormData } from "./schema";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { DatePicker } from "@/components/ui/date-picker";

export interface InquiryFormProps {
  title?: string;
  subtitle?: string;
  bookingPolicyNotice?: string;
  serviceLocationsNotice?: string;
  occasions?: Array<{ title: string }>;
  offerings?: Array<{ title: string; price?: string }>;
  initialOccasion?: string;
  onSubmitSuccess?: (data: InquiryFormData) => void;
  className?: string;
}

export function InquiryForm({
  title = "Request a Booking / Quote",
  subtitle = "Fill out your celebration details below and our team will get in touch to confirm date availability and exact pricing.",
  bookingPolicyNotice = "Submitting this inquiry form does not guarantee or confirm your booking. We will review date availability and reach out to confirm details.",
  serviceLocationsNotice = "We serve local towns across County Meath, Dublin, and surrounding areas. Locations outside our standard radius may incur an additional delivery travel fee.",
  occasions = [
    { title: "Birthdays" },
    { title: "Communions & Confirmations" },
    { title: "Gender Reveals" },
    { title: "The Bridal Era" },
    { title: "Pop-Me Gifts" },
    { title: "Christmas & Seasonal" },
  ],
  offerings = [],
  initialOccasion,
  onSubmitSuccess,
  className = "",
}: InquiryFormProps) {
  const [submittedData, setSubmittedData] = React.useState<InquiryFormData | null>(null);
  const [submissionError, setSubmissionError] = React.useState<string | null>(null);
  const [isSubmittingServer, setIsSubmittingServer] = React.useState(false);

  const defaultOccasion = initialOccasion || occasions[0]?.title || "Birthdays";

  const form = useForm({
    defaultValues: {
      name: "",
      phone: "",
      email: "",
      location: "",
      occasion: defaultOccasion,
      date: "",
      palette: "",
      fulfillment: "delivery" as "delivery" | "pickup",
      selected_products: [] as string[],
      details: "",
      agree_care: false,
      website_url: "",
    },
    onSubmit: async ({ value }) => {
      setSubmissionError(null);
      const parsed = inquirySchema.safeParse(value);

      if (!parsed.success) {
        setSubmissionError(parsed.error.issues[0]?.message || "Please check required fields.");
        return;
      }

      setIsSubmittingServer(true);
      try {
        const { data, error } = await actions.submitInquiry(parsed.data);

        if (error) {
          setSubmissionError(
            error.message || "Failed to submit booking request. Please try again.",
          );
          setIsSubmittingServer(false);
          return;
        }

        if (onSubmitSuccess) {
          onSubmitSuccess(parsed.data);
        }
        setSubmittedData(parsed.data);
      } catch (err: any) {
        setSubmissionError(err?.message || "An unexpected error occurred. Please try again.");
      } finally {
        setIsSubmittingServer(false);
      }
    },
  });

  if (submittedData) {
    return (
      <section id="inquiry" className={`mx-auto max-w-4xl py-12 ${className}`}>
        <Card className="flex flex-col items-center border-primary/30 bg-gradient-to-b from-card via-card to-secondary/30 p-8 sm:p-14 text-center shadow-lg">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-3xl shadow-xs animate-bounce">
            ✨
          </div>

          <Badge variant="champagne" size="sm" className="mt-4">
            Inquiry Received
          </Badge>

          <h3 className="mt-3 font-serif text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Thank You, {submittedData.name}!
          </h3>

          <p className="mx-auto mt-3 max-w-md text-sm sm:text-base text-muted-foreground leading-relaxed">
            We’ve recorded your booking request for your <strong>{submittedData.occasion}</strong>
            {submittedData.date ? ` on ${submittedData.date}` : ""}.
          </p>

          <div className="mt-6 w-full max-w-md rounded-2xl border border-border/80 bg-background/80 p-5 text-left text-xs sm:text-sm text-foreground/90 shadow-2xs">
            <h4 className="font-semibold text-foreground mb-2">What happens next:</h4>
            <ul className="flex flex-col gap-2 text-muted-foreground">
              <li className="flex items-start gap-2">
                <span className="text-primary font-bold">1.</span>
                <span>
                  Our styling team reviews date availability for your location (
                  {submittedData.location}).
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary font-bold">2.</span>
                <span>
                  We'll reach out to <strong>{submittedData.email}</strong> or{" "}
                  <strong>{submittedData.phone}</strong> with confirmation and bespoke palette
                  options.
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary font-bold">3.</span>
                <span>Once approved by you, your celebration date is officially reserved!</span>
              </li>
            </ul>
          </div>

          <div className="mt-8 flex flex-wrap justify-center gap-4">
            <Button
              variant="balloon"
              size="default"
              onClick={() => {
                form.reset();
                setSubmittedData(null);
              }}
            >
              Submit Another Inquiry
            </Button>
            <a href="/#occasions">
              <Button variant="balloon-outline" size="default">
                Explore More Designs &rarr;
              </Button>
            </a>
          </div>
        </Card>
      </section>
    );
  }

  return (
    <section id="inquiry" className={`mx-auto max-w-4xl py-12 ${className}`}>
      <div className="mb-8 text-center">
        <Badge variant="champagne" size="sm" className="mb-3">
          ✨ Reserve Your Date
        </Badge>
        <h2 className="font-serif text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
          {title}
        </h2>
        <p className="mx-auto mt-2 max-w-2xl text-sm sm:text-base text-muted-foreground leading-relaxed">
          {subtitle}
        </p>
      </div>

      <Card className="overflow-hidden border-border bg-card p-6 sm:p-10 shadow-lg">
        {/* Notice Disclaimers Banner */}
        <div className="mb-8 flex flex-col gap-3 rounded-2xl border border-primary/20 bg-primary/5 p-4 sm:p-5 text-xs sm:text-sm text-foreground/90">
          <div className="flex items-start gap-2.5">
            <span className="text-base leading-none">⚠️</span>
            <div>
              <strong className="font-semibold text-foreground">Booking Notice:</strong>{" "}
              {bookingPolicyNotice}
            </div>
          </div>
          <div className="flex items-start gap-2.5 border-t border-primary/10 pt-2.5">
            <span className="text-base leading-none">📍</span>
            <div>
              <strong className="font-semibold text-foreground">Service Scope:</strong>{" "}
              {serviceLocationsNotice}
            </div>
          </div>
        </div>

        {submissionError && (
          <div className="mb-6 rounded-2xl border border-destructive/40 bg-destructive/10 p-4 text-xs font-semibold text-destructive">
            {submissionError}
          </div>
        )}

        <form
          onSubmit={(e) => {
            e.preventDefault();
            e.stopPropagation();
            form.handleSubmit();
          }}
          className="flex flex-col gap-6"
        >
          {/* Honeypot Trap (Invisible to real users, catches spam bots) */}
          <div className="hidden" aria-hidden="true" style={{ display: "none" }}>
            <form.Field name="website_url">
              {(field) => (
                <input
                  type="text"
                  name={field.name}
                  value={field.state.value}
                  onChange={(e) => field.handleChange(e.target.value)}
                  tabIndex={-1}
                  autoComplete="off"
                />
              )}
            </form.Field>
          </div>

          {/* Row 1: Name & Phone */}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <form.Field
              name="name"
              validators={{
                onBlur: ({ value }) => {
                  const res = inquirySchema.shape.name.safeParse(value);
                  return res.success ? undefined : res.error.issues[0]?.message;
                },
              }}
            >
              {(field) => (
                <div className="flex flex-col gap-2">
                  <Label htmlFor={field.name}>Your Full Name *</Label>
                  <Input
                    id={field.name}
                    name={field.name}
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                    placeholder="e.g. Sarah Jenkins"
                    className={
                      field.state.meta.errors.length > 0
                        ? "border-destructive focus-visible:ring-destructive/20"
                        : ""
                    }
                  />
                  {field.state.meta.errors.length > 0 && (
                    <span className="text-xs font-medium text-destructive">
                      {field.state.meta.errors.join(", ")}
                    </span>
                  )}
                </div>
              )}
            </form.Field>

            <form.Field
              name="phone"
              validators={{
                onBlur: ({ value }) => {
                  const res = inquirySchema.shape.phone.safeParse(value);
                  return res.success ? undefined : res.error.issues[0]?.message;
                },
              }}
            >
              {(field) => (
                <div className="flex flex-col gap-2">
                  <Label htmlFor={field.name}>Phone Number *</Label>
                  <Input
                    id={field.name}
                    name={field.name}
                    type="tel"
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                    placeholder="e.g. 087 123 4567"
                    className={
                      field.state.meta.errors.length > 0
                        ? "border-destructive focus-visible:ring-destructive/20"
                        : ""
                    }
                  />
                  {field.state.meta.errors.length > 0 && (
                    <span className="text-xs font-medium text-destructive">
                      {field.state.meta.errors.join(", ")}
                    </span>
                  )}
                </div>
              )}
            </form.Field>
          </div>

          {/* Row 2: Email & Location */}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <form.Field
              name="email"
              validators={{
                onBlur: ({ value }) => {
                  const res = inquirySchema.shape.email.safeParse(value);
                  return res.success ? undefined : res.error.issues[0]?.message;
                },
              }}
            >
              {(field) => (
                <div className="flex flex-col gap-2">
                  <Label htmlFor={field.name}>Email Address *</Label>
                  <Input
                    id={field.name}
                    name={field.name}
                    type="email"
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                    placeholder="sarah@example.com"
                    className={
                      field.state.meta.errors.length > 0
                        ? "border-destructive focus-visible:ring-destructive/20"
                        : ""
                    }
                  />
                  {field.state.meta.errors.length > 0 && (
                    <span className="text-xs font-medium text-destructive">
                      {field.state.meta.errors.join(", ")}
                    </span>
                  )}
                </div>
              )}
            </form.Field>

            <form.Field
              name="location"
              validators={{
                onBlur: ({ value }) => {
                  const res = inquirySchema.shape.location.safeParse(value);
                  return res.success ? undefined : res.error.issues[0]?.message;
                },
              }}
            >
              {(field) => (
                <div className="flex flex-col gap-2">
                  <Label htmlFor={field.name}>General Town / Area *</Label>
                  <Input
                    id={field.name}
                    name={field.name}
                    value={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.value)}
                    placeholder="e.g. Navan, Ashbourne, Swords, Meath"
                    className={
                      field.state.meta.errors.length > 0
                        ? "border-destructive focus-visible:ring-destructive/20"
                        : ""
                    }
                  />
                  {field.state.meta.errors.length > 0 ? (
                    <span className="text-xs font-medium text-destructive">
                      {field.state.meta.errors.join(", ")}
                    </span>
                  ) : (
                    <span className="text-[11px] text-muted-foreground">
                      General town is fine for delivery fee calculations.
                    </span>
                  )}
                </div>
              )}
            </form.Field>
          </div>

          {/* Row 3: Occasion & Event Date */}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <form.Field name="occasion">
              {(field) => (
                <div className="flex flex-col gap-2">
                  <Label htmlFor={field.name}>Celebration Occasion</Label>
                  <select
                    id={field.name}
                    name={field.name}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    className="flex h-11 w-full rounded-2xl border border-border bg-card px-4 py-2 text-sm text-foreground shadow-xs transition-colors focus-visible:border-primary focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-primary/20"
                  >
                    {occasions.map((occ) => (
                      <option key={occ.title} value={occ.title}>
                        {occ.title}
                      </option>
                    ))}
                    <option value="Other Celebration">Other Celebration / Custom</option>
                  </select>
                </div>
              )}
            </form.Field>

            <form.Field name="date">
              {(field) => (
                <div className="flex flex-col gap-2">
                  <Label htmlFor={field.name}>Event Date</Label>
                  <DatePicker
                    id={field.name}
                    name={field.name}
                    value={field.state.value}
                    onChange={(val) => field.handleChange(val)}
                  />
                  {field.state.meta.errors.length > 0 && (
                    <p className="text-xs font-medium text-destructive">
                      {field.state.meta.errors[0]?.message || String(field.state.meta.errors[0])}
                    </p>
                  )}
                </div>
              )}
            </form.Field>
          </div>

          {/* Row 4: Color Palette & Fulfillment */}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <form.Field name="palette">
              {(field) => (
                <div className="flex flex-col gap-2">
                  <Label htmlFor={field.name}>Preferred Color Palette</Label>
                  <Input
                    id={field.name}
                    name={field.name}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    placeholder="e.g. Sage green & champagne gold, Blush & nude"
                  />
                </div>
              )}
            </form.Field>

            <form.Field name="fulfillment">
              {(field) => (
                <div className="flex flex-col gap-2">
                  <Label htmlFor={field.name}>Fulfillment Preference</Label>
                  <select
                    id={field.name}
                    name={field.name}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value as "delivery" | "pickup")}
                    className="flex h-11 w-full rounded-2xl border border-border bg-card px-4 py-2 text-sm text-foreground shadow-xs transition-colors focus-visible:border-primary focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-primary/20"
                  >
                    <option value="delivery">Delivery & On-Site Setup at Venue</option>
                    <option value="pickup">Customer Collection / Pickup</option>
                  </select>
                </div>
              )}
            </form.Field>
          </div>

          {/* Offerings Checkboxes */}
          {offerings && offerings.length > 0 && (
            <form.Field name="selected_products">
              {(field) => (
                <div className="flex flex-col gap-2.5">
                  <Label>Package Offerings of Interest (Optional)</Label>
                  <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-2">
                    {offerings.map((item) => {
                      const isSelected = field.state.value.includes(item.title);
                      return (
                        <label
                          key={item.title}
                          className={`flex cursor-pointer items-center justify-between rounded-2xl border p-3.5 transition-all ${
                            isSelected
                              ? "border-primary bg-primary/10 shadow-xs"
                              : "border-border/80 bg-background/60 hover:border-primary/40 hover:bg-secondary/40"
                          }`}
                        >
                          <span className="flex items-center gap-2.5">
                            <input
                              type="checkbox"
                              checked={isSelected}
                              onChange={(e) => {
                                const next = e.target.checked
                                  ? [...field.state.value, item.title]
                                  : field.state.value.filter((t) => t !== item.title);
                                field.handleChange(next);
                              }}
                              className="h-4 w-4 rounded-md border-border accent-primary"
                            />
                            <span className="text-xs sm:text-sm font-medium text-foreground">
                              {item.title}
                            </span>
                          </span>
                          {item.price && (
                            <span className="text-xs font-semibold text-primary">{item.price}</span>
                          )}
                        </label>
                      );
                    })}
                  </div>
                </div>
              )}
            </form.Field>
          )}

          {/* Custom Notes / Vision */}
          <form.Field name="details">
            {(field) => (
              <div className="flex flex-col gap-2">
                <Label htmlFor={field.name}>Event Vision & Custom Notes</Label>
                <Textarea
                  id={field.name}
                  name={field.name}
                  value={field.state.value}
                  onChange={(e) => field.handleChange(e.target.value)}
                  rows={4}
                  placeholder="Tell us about the venue, custom vinyl names (e.g. 'Emma is One'), milestone numbers, or specific theme..."
                />
              </div>
            )}
          </form.Field>

          {/* Balloon Care & Store Line Rule Agreement Checkbox */}
          <form.Field
            name="agree_care"
            validators={{
              onChange: ({ value }) => {
                const res = inquirySchema.shape.agree_care.safeParse(value);
                return res.success ? undefined : res.error.issues[0]?.message;
              },
            }}
          >
            {(field) => (
              <div
                className={`rounded-2xl border p-4 transition-colors ${
                  field.state.meta.errors.length > 0
                    ? "border-destructive/60 bg-destructive/5"
                    : "border-border/80 bg-secondary/30"
                }`}
              >
                <label className="flex cursor-pointer items-start gap-3">
                  <input
                    type="checkbox"
                    checked={field.state.value}
                    onBlur={field.handleBlur}
                    onChange={(e) => field.handleChange(e.target.checked)}
                    className="mt-1 h-4 w-4 rounded-md border-border accent-primary"
                  />
                  <span className="text-xs text-foreground/90 leading-relaxed">
                    I understand and accept <strong>The Store Line Balloon Care Policy</strong>:
                    balloons are sensitive to temperature, sunlight, and sharp hazards. Once
                    delivered, installed, or collected, care responsibility belongs to the client.
                  </span>
                </label>
                {field.state.meta.errors.length > 0 && (
                  <p className="mt-2 text-xs font-semibold text-destructive">
                    {field.state.meta.errors.join(", ")}
                  </p>
                )}
              </div>
            )}
          </form.Field>

          {/* Submit Action */}
          <form.Subscribe selector={(state) => [state.canSubmit, state.isSubmitting]}>
            {([canSubmit, isSubmitting]) => (
              <Button
                type="submit"
                variant="balloon"
                size="lg"
                disabled={!canSubmit || isSubmitting || isSubmittingServer}
                className="w-full text-base font-semibold"
              >
                {isSubmitting || isSubmittingServer
                  ? "Submitting Request..."
                  : "Submit Booking Request ✨"}
              </Button>
            )}
          </form.Subscribe>

          <p className="text-center text-xs text-muted-foreground">
            Prefer to speak directly? Feel free to call or message Luxe Bear Studio anytime.
          </p>
        </form>
      </Card>
    </section>
  );
}

export default InquiryForm;
