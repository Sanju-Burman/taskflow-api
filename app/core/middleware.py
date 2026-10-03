import logging
import time
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("taskflow")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log request duration and add performance headers."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = (time.perf_counter() - start_time) * 1000
        response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
        return response


def setup_middleware(app: FastAPI) -> None:
    app.add_middleware(RequestLoggingMiddleware)
