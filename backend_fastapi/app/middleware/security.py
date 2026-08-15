from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, PlainTextResponse
from time import time
from typing import Callable
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        # Strict Transport Security -- only add when HTTPS redirect is enabled
        if settings.ENABLE_HTTPS_REDIRECT:
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=()"
        # Minimal CSP - adapt for your frontend host
        response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-inline' data:; img-src * data:; connect-src 'self'"
        return response


class SimpleRateLimitMiddleware(BaseHTTPMiddleware):
    """A simple in-memory per-IP sliding window rate limiter.

    Note: This is suitable for development and single-process deployments only.
    For production, use a centralized store (Redis) with a robust library.
    """

    def __init__(self, app, calls_per_minute: int = 60):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.window = 60.0
        self.storage = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        client = request.client.host if request.client else "unknown"
        now = time()
        q = self.storage.get(client, [])
        # remove old entries
        q = [t for t in q if t > now - self.window]
        if len(q) >= self.calls_per_minute:
            retry_after = int(q[0] + self.window - now) if q else 60
            logger.warning("Rate limit exceeded for %s", client)
            return PlainTextResponse("Too Many Requests", status_code=429, headers={"Retry-After": str(retry_after)})
        q.append(now)
        self.storage[client] = q
        return await call_next(request)


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        max_size = settings.MAX_REQUEST_SIZE
        content_length = request.headers.get("content-length")
        if content_length is not None:
            try:
                if int(content_length) > max_size:
                    return PlainTextResponse("Request Entity Too Large", status_code=413)
            except ValueError:
                pass
        return await call_next(request)
