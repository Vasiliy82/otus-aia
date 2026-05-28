from __future__ import annotations

import logging
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from backend.config import (
    OTEL_EXPORTER_OTLP_ENDPOINT,
    OTEL_SERVICE_NAME,
    OTEL_TRACES_ENABLED,
)

logger = logging.getLogger(__name__)

_tracer: Any | None = None
_tracing_enabled = False


class _NoopSpan:
    def set_attribute(self, key: str, value: Any) -> None:
        return None


class _NoopTracer:
    @contextmanager
    def start_as_current_span(self, name: str, **kwargs: Any) -> Iterator[_NoopSpan]:
        yield _NoopSpan()


def setup_tracing(app: Any | None = None) -> bool:
    global _tracer, _tracing_enabled

    if not OTEL_TRACES_ENABLED:
        _tracer = _NoopTracer()
        _tracing_enabled = False
        logger.info("OpenTelemetry tracing disabled (OTEL_TRACES_ENABLED=false)")
        return False

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({"service.name": OTEL_SERVICE_NAME})
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=OTEL_EXPORTER_OTLP_ENDPOINT, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer(__name__)
        _tracing_enabled = True

        if app is not None:
            FastAPIInstrumentor.instrument_app(app, excluded_urls="/health")

        logger.info(
            "OpenTelemetry tracing enabled service=%s endpoint=%s",
            OTEL_SERVICE_NAME,
            OTEL_EXPORTER_OTLP_ENDPOINT,
        )
        return True
    except Exception as exc:
        logger.warning("OpenTelemetry setup failed, tracing disabled: %s", exc)
        _tracer = _NoopTracer()
        _tracing_enabled = False
        return False


def get_tracer() -> Any:
    global _tracer
    if _tracer is None:
        setup_tracing()
    return _tracer


def format_trace_id(trace_id: int) -> str:
    return format(trace_id, "032x")


@contextmanager
def traced_span(name: str, *, attributes: dict[str, Any] | None = None) -> Iterator[Any]:
    tracer = get_tracer()
    with tracer.start_as_current_span(name) as span:
        if attributes and hasattr(span, "set_attribute"):
            for key, value in attributes.items():
                if value is not None:
                    span.set_attribute(key, value)
        yield span


def current_trace_id_hex() -> str | None:
    if not _tracing_enabled:
        return None
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        ctx = span.get_span_context()
        if ctx.trace_id == 0:
            return None
        return format_trace_id(ctx.trace_id)
    except Exception:
        return None
