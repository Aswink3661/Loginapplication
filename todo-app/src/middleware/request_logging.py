import logging
from time import perf_counter
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from src.utils.logger import get_logger
from src.utils.telemetry import (
    emit_event,
    record_http_request,
    set_current_span_attributes,
    start_span,
)

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log one structured record for every HTTP request."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        started_at = perf_counter()
        span_attributes = {
            "http.request_id": request_id,
            "http.request.method": request.method,
            "url.path": request.url.path,
            "url.query": request.url.query,
        }

        with start_span("todo.http.request", span_attributes):
            set_current_span_attributes(span_attributes)

            try:
                response = await call_next(request)
            except Exception:
                duration_ms = self._duration_ms(started_at)
                context = self._log_context(
                    request=request,
                    request_id=request_id,
                    status_code=500,
                    duration_ms=duration_ms,
                )
                emit_event("http.request.failed", context)
                record_http_request(
                    method=request.method,
                    path=request.url.path,
                    status_code=500,
                    duration_ms=duration_ms,
                )
                logger.exception(
                    "http.request.failed",
                    extra=context,
                )
                raise

            response.headers["X-Request-ID"] = request_id
            status_code = response.status_code
            duration_ms = self._duration_ms(started_at)
            context = self._log_context(
                request=request,
                request_id=request_id,
                status_code=status_code,
                duration_ms=duration_ms,
            )
            set_current_span_attributes(
                {
                    "http.response.status_code": status_code,
                    "http.server.request.duration_ms": duration_ms,
                }
            )
            emit_event("http.request.completed", context)
            record_http_request(
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration_ms=duration_ms,
            )
            log_level = logging.WARNING if status_code >= 400 else logging.INFO
            logger.log(
                log_level,
                "http.request.completed",
                extra=context,
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
