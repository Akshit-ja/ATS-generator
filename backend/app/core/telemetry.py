"""
OpenTelemetry configuration for distributed tracing and metrics.
"""
import os
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from prometheus_client import start_http_server
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor
# from opentelemetry.instrumentation.httpx import HTTPXInstrumentor  # Temporarily disabled

# Constants
SERVICE_NAME = "resume-ai-generator"
PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", "8099"))
OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT", "http://jaeger:4317")

# Custom metrics
api_latency = None
gpt_response_time = None
celery_task_duration = None
redis_cache_hits = None
redis_cache_misses = None
error_counter = None
api_cost_counter = None

def setup_telemetry():
    """Initialize OpenTelemetry with trace and metrics providers."""
    # Create a resource with service information
    resource = Resource.create({"service.name": SERVICE_NAME})
    
    # Set up tracing
    trace_provider = TracerProvider(resource=resource)
    
    # Configure OTLP exporter for sending traces to a collector
    otlp_exporter = OTLPSpanExporter(endpoint=OTLP_ENDPOINT, insecure=True)
    trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    
    # Set the global trace provider
    trace.set_tracer_provider(trace_provider)
    
    # Set up metrics with Prometheus exporter
    prometheus_reader = PrometheusMetricReader()
    metric_readers = [prometheus_reader]
    
    # Create and set the meter provider
    metrics_provider = MeterProvider(resource=resource, metric_readers=metric_readers)
    metrics.set_meter_provider(metrics_provider)
    
    # Start Prometheus HTTP server for metrics scraping
    start_http_server(port=PROMETHEUS_PORT)
    
    # Create custom metrics
    _setup_custom_metrics()
    
    return trace_provider, metrics_provider

def _setup_custom_metrics():
    """Set up custom metrics for monitoring specific aspects of the application."""
    global api_latency, gpt_response_time, celery_task_duration, redis_cache_hits, redis_cache_misses, error_counter, api_cost_counter
    
    meter = metrics.get_meter(__name__)
    
    # API latency histogram
    api_latency = meter.create_histogram(
        name="api_latency",
        description="Latency of API endpoints in seconds",
        unit="s",
    )
    
    # GPT response time
    gpt_response_time = meter.create_histogram(
        name="gpt_response_time",
        description="Time taken for GPT-4 API to respond in seconds",
        unit="s",
    )
    
    # Celery task duration
    celery_task_duration = meter.create_histogram(
        name="celery_task_duration",
        description="Duration of Celery tasks in seconds",
        unit="s",
    )
    
    # Redis cache metrics
    redis_cache_hits = meter.create_counter(
        name="redis_cache_hits",
        description="Number of Redis cache hits",
    )
    
    redis_cache_misses = meter.create_counter(
        name="redis_cache_misses",
        description="Number of Redis cache misses",
    )
    
    # Error counter
    error_counter = meter.create_counter(
        name="error_count",
        description="Number of errors by type",
    )
    
    # API cost counter (for OpenAI)
    api_cost_counter = meter.create_counter(
        name="api_cost",
        description="Cost of API calls in USD",
        unit="$",
    )

def instrument_app(app, db_engine=None, redis_client=None):
    """Instrument the FastAPI application and its dependencies."""
    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app, tracer_provider=trace.get_tracer_provider())
    
    # Instrument SQLAlchemy if engine is provided
    if db_engine:
        SQLAlchemyInstrumentor().instrument(engine=db_engine)
    
    # Instrument Redis if client is provided
    if redis_client:
        RedisInstrumentor().instrument()
    
    # Instrument HTTPX for external API calls (disabled)
    # HTTPXInstrumentor().instrument()
    
    # Instrument Celery for task monitoring
    CeleryInstrumentor().instrument()

def get_tracer(name=SERVICE_NAME):
    """Get a tracer for creating custom spans."""
    return trace.get_tracer(name)

# Helper functions for custom instrumentation

def track_gpt_request(prompt_tokens, completion_tokens, model, duration):
    """Track GPT request metrics including cost."""
    # Record response time
    gpt_response_time.record(duration, {"model": model})
    
    # Calculate and record cost based on model and tokens
    # Pricing as of knowledge cutoff, adjust as needed
    cost = 0
    if model == "gpt-4":
        cost = (prompt_tokens * 0.03 + completion_tokens * 0.06) / 1000
    elif model == "gpt-3.5-turbo":
        cost = (prompt_tokens * 0.0015 + completion_tokens * 0.002) / 1000
    
    if cost > 0:
        api_cost_counter.add(cost, {"model": model})

def track_redis_cache(hit):
    """Track Redis cache hit/miss."""
    if hit:
        redis_cache_hits.add(1)
    else:
        redis_cache_misses.add(1)

def track_error(error_type):
    """Track application errors by type."""
    error_counter.add(1, {"error_type": error_type})