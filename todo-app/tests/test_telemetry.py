from src.config.settings import Settings
from src.utils.telemetry import _otlp_exporter_kwargs


def test_otlp_exporter_kwargs_include_headers_for_new_relic() -> None:
    settings = Settings(
        OTEL_EXPORTER_OTLP_ENDPOINT="https://otlp.eu01.nr-data.net:4317",
        OTEL_EXPORTER_OTLP_HEADERS="api-key=test-license-key",
    )

    kwargs = _otlp_exporter_kwargs(settings)

    assert kwargs["endpoint"] == "https://otlp.eu01.nr-data.net:4317"
    assert kwargs["headers"] == "api-key=test-license-key"
    assert "insecure" not in kwargs


def test_otlp_exporter_kwargs_mark_plain_http_as_insecure() -> None:
    settings = Settings(OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317")

    kwargs = _otlp_exporter_kwargs(settings)

    assert kwargs["insecure"] is True
