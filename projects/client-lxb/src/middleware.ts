import { defineMiddleware } from "astro:middleware";
import { checkRateLimit } from "@/lib/rate-limit";

export const onRequest = defineMiddleware(async (context, next) => {
  const { pathname } = context.url;

  // Protect inquiry submission endpoint against rapid IP floods
  if (pathname === "/api/inquiry" && context.request.method === "POST") {
    const forwarded = context.request.headers.get("x-forwarded-for");
    const ip = forwarded
      ? forwarded.split(",")[0].trim()
      : context.clientAddress || "anonymous";

    const limit = checkRateLimit(`ip:${ip}`, {
      maxRequests: 5,
      windowSeconds: 60,
    });

    if (!limit.allowed) {
      return new Response(
        JSON.stringify({
          error: "Too many requests. Please wait before submitting another inquiry.",
          retryAfter: limit.retryAfter,
        }),
        {
          status: 429,
          headers: {
            "Content-Type": "application/json",
            "Retry-After": String(limit.retryAfter ?? 60),
          },
        },
      );
    }
  }

  return next();
});
