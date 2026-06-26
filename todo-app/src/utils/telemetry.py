from __future__ import annotations

import logging
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from typing import Any, Iterator, Mapping
from urllib.parse import urlparse

from src.config.settings import Settings, get_settings

try:
    from opentelemetry import _logs, metrics, trace
    from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.logging import LoggingInstrumentor
    from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
    from opentelemetry.sdk._logs.export import (
        BatchLogRecordProcessor,
        ConsoleLogExporter,
        SimpleLogRecordProcessor,
    )
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter, SimpleSpanProcessor
except ImportError as exc:  # pragma: no cover - exercised in environments without OTEL packages
    _OTEL_IMPORT_ERROR: ImportError | None = exc
    _logs = None
    metrics = None
    trace = None
    OTLPLogExporter = None
    OTLPMetricExporter = None
    OTLPSpanExporter = None
    FastAPIInstrumentor = None
    LoggingInstrumentor = None
    LoggerProvider = None
    LoggingHandler = None
    BatchLogRecordProcessor = None
    ConsoleLogExporter = None
    SimpleLogRecordProcessor = None
    MeterProvider = None
    ConsoleMetricExporter = None
    PeriodicExportingMetricReader = None
    Resource = None
    TracerProvider = None
    BatchSpanProcessor = None
    ConsoleSpanExporter = None
    SimpleSpanProcessor = None
else:
    _OTEL_IMPORT_ERROR = None


logger = logging.getLogger(__name__)
_OTEL_LOG_HANDLER_ATTR = "_loginapplication_otel_handler"


@dataclass(slots=True)
class TelemetryState:
    """Track process-wide OpenTelemetry configuration."""

    configured: bool = False
    enabled: bool = False
    available: bool = _OTEL_IMPORT_ERROR is None
    tracer_provider: Any = None
    meter_provider: Any = None
    logger_provider: Any = None
    http_request_counter: Any = None
    http_request_duration: Any = None
    todo_operation_counter: Any = None


class NoOpSpan:
    """Small span stand-in used when OpenTelemetry is disabled or unavailable."""

    def set_attribute(self, key: str, value: Any) -> None:
        return None

    def add_event(self, name: str, attributes: Mapping[str, Any] | None = None) -> None:
        return None

    def record_exception(self, exception: BaseException) -> None:
        return None

    def is_recording(self) -> bool:
        return False


_state = TelemetryState()


def configure_telemetry(app: Any | None = None, settings: Settings | None = None) -> TelemetryState:
    """Configure OpenTelemetry for Metrics, Events, Logs, and Traces."""
    settings = settings or get_settings()

    if not settings.OTEL_ENABLED:
        _state.configured = True
        _state.enabled = False
        return _state

    if _OTEL_IMPORT_ERROR is not None:
        if not _state.configured:
            logger.warning("OpenTelemetry packages are not installed; telemetry export is disabled.")
        _state.configured = True
        _state.enabled = False
        _instrument_fastapi_app(app)
        return _state

    if not _state.configured:
        resource = _build_resource(settings)
        _configure_traces(settings=settings, resource=resource)
        _configure_metrics(settings=settings, resource=resource)
        _configure_logs(settings=settings, resource=resource)
        _configure_log_correlation()
        _state.configured = True
        _state.enabled = True

    _instrument_fastapi_app(app)
    _ensure_metric_instruments()
    return _state


def telemetry_enabled() -> bool:
    return _state.enabled and _OTEL_IMPORT_ERROR is None


@contextmanager
def start_span(name: str, attributes: Mapping[str, Any] | None = None) -> Iterator[Any]:
    """Start a current span when telemetry is active, otherwise yield a no-op span."""
    if not telemetry_enabled() or trace is None:
        yield NoOpSpan()
        return

    tracer = trace.get_tracer("loginapplication.todo")
    with tracer.start_as_current_span(name, attributes=_clean_attributes(attributes)) as span:
        yield span


def set_current_span_attributes(attributes: Mapping[str, Any] | None) -> None:
    if not telemetry_enabled() or trace is None:
        return

    span = trace.get_current_span()
    if span is None or not span.is_recording():
        return

    for key, value in _clean_attributes(attributes).items():
        span.set_attribute(key, value)


def emit_event(name: str, attributes: Mapping[str, Any] | None = None, *, log_event: bool = False) -> None:
    """Record an event on the current span, optionally mirroring it as a structured log."""
    cleaned = _clean_attributes(attributes)

    if telemetry_enabled() and trace is not None:
        span = trace.get_current_span()
        if span is not None and span.is_recording():
            span.add_event(name, attributes=cleaned)

    if log_event:
        logging.getLogger("src.telemetry.events").info(
            name,
            extra={"event": name, "event_name": name, **cleaned},
        )


def record_http_request(
    *,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
) -> None:
    if not telemetry_enabled():
        return

    _ensure_metric_instruments()
    attributes = _clean_attributes(
        {
            "http.request.method": method,
            "url.path": path,
            "http.response.status_code": status_code,
        }
    )

    if _state.http_request_counter is not None:
        _state.http_request_counter.add(1, attributes)
    if _state.http_request_duration is not None:
        _state.http_request_duration.record(duration_ms, attributes)


def record_todo_operation(
    operation: str,
    status: str,
    attributes: Mapping[str, Any] | None = None,
) -> None:
    if not telemetry_enabled():
        return

    _ensure_metric_instruments()
    metric_attributes = {
        "todo.operation": operation,
        "todo.status": status,
        **(attributes or {}),
    }

    if _state.todo_operation_counter is not None:
        _state.todo_operation_counter.add(1, _clean_attributes(metric_attributes))


def force_flush_telemetry(timeout_millis: int = 5_000) -> None:
    """Best-effort flush for app shutdown without tearing down reusable global providers."""
    for provider in (_state.tracer_provider, _state.meter_provider, _state.logger_provider):
        if provider is not None and hasattr(provider, "force_flush"):
            with suppress(Exception):
                provider.force_flush(timeout_millis=timeout_millis)


def _build_resource(settings: Settings) -> Any:
    if Resource is None:
        return None

    return Resource.create(
        {
            "service.name": settings.OTEL_SERVICE_NAME or settings.APP_NAME,
            "service.namespace": settings.OTEL_SERVICE_NAMESPACE,
            "service.version": settings.APP_VERSION,
            "deployment.environment": settings.ENVIRONMENT,
        }
    )


def _configure_traces(*, settings: Settings, resource: Any) -> None:
    if TracerProvider is None or trace is None:
        return

    provider = TracerProvider(resource=resource)
    processor = _build_span_processor(settings)
    if processor is not None:
        provider.add_span_processor(processor)

    trace.set_tracer_provider(provider)
    _state.tracer_provider = provider


def _configure_metrics(*, settings: Settings, resource: Any) -> None:
    if MeterProvider is None or metrics is None:
        return

    reader = _build_metric_reader(settings)
    readers = [reader] if reader is not None else []
    provider = MeterProvider(resource=resource, metric_readers=readers)

    metrics.set_meter_provider(provider)
    _state.meter_provider = provider


def _configure_logs(*, settings: Settings, resource: Any) -> None:
    if LoggerProvider is None or _logs is None:
        return

    provider = LoggerProvider(resource=resource)
    processor = _build_log_processor(settings)
    if processor is not None:
        provider.add_log_record_processor(processor)

    _logs.set_logger_provider(provider)
    _state.logger_provider = provider

    if LoggingHandler is not None and processor is not None:
        root_logger = logging.getLogger()
        _remove_otel_log_handlers(root_logger)
        handler = LoggingHandler(level=_resolve_level(settings.LOG_LEVEL), logger_provider=provider)
        setattr(handler, _OTEL_LOG_HANDLER_ATTR, True)
        root_logger.addHandler(handler)


def _configure_log_correlation() -> None:
    if LoggingInstrumentor is None:
        return

    with suppress(Exception):
        LoggingInstrumentor().instrument(
            set_logging_format=False,
            inject_trace_context=True,
            enable_log_auto_instrumentation=False,
        )


def _instrument_fastapi_app(app: Any | None) -> None:
    if app is None or FastAPIInstrumentor is None:
        return

    if getattr(app.state, "_otel_instrumented", False):
        return

    FastAPIInstrumentor.instrument_app(app, excluded_urls="/health")
    app.state._otel_instrumented = True


def _build_span_processor(settings: Settings) -> Any | None:
    if settings.OTEL_EXPORTER == "none":
        return None
    if settings.OTEL_EXPORTER == "console" and ConsoleSpanExporter is not None:
        return SimpleSpanProcessor(ConsoleSpanExporter())
    if settings.OTEL_EXPORTER == "otlp" and OTLPSpanExporter is not None:
        return BatchSpanProcessor(OTLPSpanExporter(**_otlp_exporter_kwargs(settings)))
    return None


def _build_metric_reader(settings: Settings) -> Any | None:
    if settings.OTEL_EXPORTER == "none":
        return None
    if settings.OTEL_EXPORTER == "console" and ConsoleMetricExporter is not None:
        return PeriodicExportingMetricReader(
            ConsoleMetricExporter(),
            export_interval_millis=settings.OTEL_METRIC_EXPORT_INTERVAL_MS,
        )
    if settings.OTEL_EXPORTER == "otlp" and OTLPMetricExporter is not None:
        return PeriodicExportingMetricReader(
            OTLPMetricExporter(**_otlp_exporter_kwargs(settings)),
            export_interval_millis=settings.OTEL_METRIC_EXPORT_INTERVAL_MS,
        )
    return None


def _build_log_processor(settings: Settings) -> Any | None:
    if settings.OTEL_EXPORTER == "none":
        return None
    if settings.OTEL_EXPORTER == "console" and ConsoleLogExporter is not None:
        return SimpleLogRecordProcessor(ConsoleLogExporter())
    if settings.OTEL_EXPORTER == "otlp" and OTLPLogExporter is not None:
        return BatchLogRecordProcessor(OTLPLogExporter(**_otlp_exporter_kwargs(settings)))
    return None


def _ensure_metric_instruments() -> None:
    if not telemetry_enabled() or metrics is None:
        return

    meter = metrics.get_meter("loginapplication.todo")
    if _state.http_request_counter is None:
        _state.http_request_counter = meter.create_counter(
            name="http.server.request.count",
            description="Number of HTTP requests handled by the Todo API.",
            unit="{request}",
        )
    if _state.http_request_duration is None:
        _state.http_request_duration = meter.create_histogram(
            name="http.server.request.duration",
            description="HTTP request duration measured at the application middleware.",
            unit="ms",
        )
    if _state.todo_operation_counter is None:
        _state.todo_operation_counter = meter.create_counter(
            name="todo.operation.count",
            description="Number of Todo domain operations.",
            unit="{operation}",
        )


def _otlp_exporter_kwargs(settings: Settings) -> dict[str, Any]:
    endpoint = settings.OTEL_EXPORTER_OTLP_ENDPOINT
    parsed = urlparse(endpoint)
    kwargs: dict[str, Any] = {"endpoint": endpoint}
    if settings.OTEL_EXPORTER_OTLP_HEADERS:
        kwargs["headers"] = settings.OTEL_EXPORTER_OTLP_HEADERS
    if parsed.scheme == "http":
        kwargs["insecure"] = True
    return kwargs


def _resolve_level(level_name: str) -> int:
    return getattr(logging, level_name.upper(), logging.INFO)


def _remove_otel_log_handlers(root_logger: logging.Logger) -> None:
    for handler in list(root_logger.handlers):
        if getattr(handler, _OTEL_LOG_HANDLER_ATTR, False):
            root_logger.removeHandler(handler)
            handler.close()


def _clean_attributes(attributes: Mapping[str, Any] | None) -> dict[str, Any]:
    if not attributes:
        return {}

    cleaned: dict[str, Any] = {}
    for key, value in attributes.items():
        cleaned_value = _clean_attribute_value(value)
        if cleaned_value is not None:
            cleaned[str(key)] = cleaned_value
    return cleaned


def _clean_attribute_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple)):
        values = [_clean_attribute_value(item) for item in value]
        return [item for item in values if item is not None]
    return str(value)
