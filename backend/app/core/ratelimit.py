# backend/app/core/ratelimit.py
# In-process, per-client sliding-window rate limiting plus the helpers
# that derive a client key from the request.

from __future__ import annotations

import threading
import time
from collections import deque

from fastapi import Request

# Mapping of supported rate-limit units to their duration in seconds.
_UNIT_SECONDS: dict[str, float] = {
    "second": 1.0,
    "seconds": 1.0,
    "minute": 60.0,
    "minutes": 60.0,
    "hour": 3600.0,
    "hours": 3600.0,
}


class RateLimiter:
    """Thread-safe sliding-window rate limiter.

    Each key (typically a client IP) may make at most ``limit`` requests
    per ``window_seconds``.  Old timestamps are pruned on every check and
    at most ``max_keys`` clients are tracked; the least-recently-seen
    client is evicted at capacity, which keeps memory bounded even under
    high client cardinality.
    """

    def __init__(
        self,
        limit: int,
        window_seconds: float,
        max_keys: int = 1024,
    ) -> None:
        self.limit = limit
        self.window = window_seconds
        self.max_keys = max_keys
        self._hits: dict[str, deque[float]] = {}
        self._last_seen: dict[str, float] = {}
        self._lock = threading.Lock()

    def _evict_lru(self) -> None:
        """Drop the least-recently-seen client to free capacity."""
        oldest = min(self._last_seen, key=lambda key: self._last_seen[key])
        self._hits.pop(oldest, None)
        self._last_seen.pop(oldest, None)

    def is_limited(self, key: str) -> bool:
        """Record a hit for ``key`` and report whether it is over budget."""
        now = time.monotonic()
        cutoff = now - self.window
        with self._lock:
            hits = self._hits.get(key)
            if hits is None:
                if len(self._hits) >= self.max_keys:
                    self._evict_lru()
                hits = deque()
                self._hits[key] = hits
            while hits and hits[0] <= cutoff:
                hits.popleft()
            self._last_seen[key] = now
            if len(hits) < self.limit:
                hits.append(now)
                return False
            return True


def parse_rate_limit(rate: str) -> tuple[int, float] | None:
    """Parse a rate string such as ``'30/minute'``.

    Args:
        rate: Value of ``SENTIMENTA_RATE_LIMIT``.

    Returns:
        ``(count, window_seconds)`` or ``None`` when rate limiting is
        disabled (empty string or ``'0'``).

    Raises:
        ValueError: If the string is not a recognised rate format.
    """
    rate = rate.strip()
    if not rate or rate == "0":
        return None
    parts = rate.split("/", 1)
    if len(parts) != 2:
        raise ValueError(f"Invalid rate format: {rate!r}")
    count_text = parts[0].strip()
    unit = parts[1].strip().lower()
    if not count_text.isdigit():
        raise ValueError(f"Invalid rate count: {count_text!r}")
    seconds = _UNIT_SECONDS.get(unit)
    if seconds is None:
        raise ValueError(f"Unknown rate unit: {unit!r}")
    return int(count_text), seconds


def client_ip(request: Request, trust_proxy: bool) -> str:
    """Return the best-effort client IP used to key the rate limiter.

    When ``trust_proxy`` is enabled the first ``X-Forwarded-For`` entry
    (or ``X-Real-IP``) is used.  Only enable it when the application runs
    behind a trusted reverse proxy that overwrites these headers;
    otherwise they are client-controlled and could be spoofed.
    """
    if trust_proxy:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
    if request.client is not None:
        return request.client.host
    return "unknown"
