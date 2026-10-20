interface RateLimitRecord {
  count: number;
  resetAt: number;
}

export interface RateLimitOptions {
  maxRequests?: number;
  windowSeconds?: number;
}

export interface RateLimitResult {
  allowed: boolean;
  remaining: number;
  resetAt: number;
  retryAfter?: number;
}

const store = new Map<string, RateLimitRecord>();

/**
 * Periodically purge expired records to prevent unbounded memory growth.
 */
function cleanupExpired() {
  const now = Date.now();
  for (const [key, record] of store.entries()) {
    if (now >= record.resetAt) {
      store.delete(key);
    }
  }
}

// Clean up memory store every 5 minutes
if (typeof setInterval !== "undefined") {
  const cleanupTimer = setInterval(cleanupExpired, 5 * 60 * 1000);
  if (cleanupTimer.unref) {
    cleanupTimer.unref();
  }
}

/**
 * Check and record an action against an in-memory rate limit.
 *
 * @param key Unique identifier (e.g. `ip:127.0.0.1` or `email:user@example.com`)
 * @param options maxRequests and windowSeconds
 */
export function checkRateLimit(
  key: string,
  options: RateLimitOptions = {},
): RateLimitResult {
  const maxRequests = options.maxRequests ?? 5;
  const windowSeconds = options.windowSeconds ?? 60;
  const now = Date.now();
  const existing = store.get(key);

  if (!existing || now >= existing.resetAt) {
    const resetAt = now + windowSeconds * 1000;
    store.set(key, { count: 1, resetAt });
    return {
      allowed: true,
      remaining: maxRequests - 1,
      resetAt,
    };
  }

  if (existing.count >= maxRequests) {
    return {
      allowed: false,
      remaining: 0,
      resetAt: existing.resetAt,
      retryAfter: Math.ceil((existing.resetAt - now) / 1000),
    };
  }

  existing.count += 1;
  return {
    allowed: true,
    remaining: maxRequests - existing.count,
    resetAt: existing.resetAt,
  };
}
