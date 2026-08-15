from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class SimpleRateLimiter(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Dev-only placeholder: allow all
        return await call_next(request)
