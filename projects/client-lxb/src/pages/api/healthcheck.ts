import type { APIContext, APIRoute } from "astro";

export const prerender = false;

export const GET: APIRoute = async () => {
  return new Response(
    JSON.stringify({
      healthy: true,
      timestamp: new Date().toISOString(),
    }),
    {
      status: 200,
      headers: {
        "Content-Type": "application/json",
      },
    },
  );
};

export function HEAD(_context: APIContext): Response {
  return new Response(null, {
    status: 204,
  });
}
