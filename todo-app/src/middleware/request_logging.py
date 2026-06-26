import logging
from time import perf_counter
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from src.utils.logger import get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log one structured record for every HTTP request."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        started_at = perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "http.request.failed",
                extra=self._log_context(
                    request=request,
                    request_id=request_id,
                    status_code=500,
                    duration_ms=self._duration_ms(started_at),
                ),
            )
            raise

        response.headers["X-Request-ID"] = request_id
        status_code = response.status_code
        log_level = logging.WARNING if status_code >= 400 else logging.INFO
        logger.log(
            log_level,
            "http.request.completed",
            extra=self._log_context(
                request=request,
                request_id=request_id,
                status_code=status_code,
                duration_ms=self._duration_ms(started_at),
            ),
        )

        return response

    @staticmethod
    def _duration_ms(started_at: float) -> float:
        return round((perf_counter() - started_at) * 1000, 2)

    @staticmethod
    def _log_context(
        *,
        request: Request,
        request_id: str,
        status_code: int,
        duration_ms: float,
    ) -> dict:
        client_host = request.client.host if request.client else None
        return {
            "event": "http.request",
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query": request.url.query,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "client_ip": client_host,
            "user_agent": request.headers.get("user-agent"),
        }
