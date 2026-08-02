from __future__ import annotations

import threading
import time


class TokenBucketRateLimiter:
    """Per-client token bucket rate limiter (stdlib only, ADR-0023).

    Each client key gets `capacity` tokens refilled at `capacity` per
    minute. A request consumes one token; when none remain, it is
    rate-limited (HTTP 429) until a token refills.
    """

    def __init__(self, requests_per_minute: int, now_fn=time.monotonic) -> None:
        self.capacity = requests_per_minute
        self.refill_per_second = requests_per_minute / 60.0
        self._now = now_fn
        self._buckets: dict[str, tuple[float, float]] = {}  # key -> (tokens, last_refill)
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = self._now()
        with self._lock:
            tokens, last = self._buckets.get(key, (self.capacity, now))
            elapsed = max(0.0, now - last)
            tokens = min(self.capacity, tokens + elapsed * self.refill_per_second)
            if tokens >= 1.0:
                self._buckets[key] = (tokens - 1.0, now)
                return True
            self._buckets[key] = (tokens, now)
            return False
