"""
Prometheus configuration module for metrics export.
This module sets up the Prometheus exporter and provides endpoints for metrics scraping.
"""

import logging
from fastapi import FastAPI, APIRouter
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Create a router for Prometheus metrics
metrics_router = APIRouter()

@metrics_router.get("/metrics")
async def metrics():
    """
    Endpoint for Prometheus to scrape metrics.
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

def setup_prometheus_endpoint(app: FastAPI):
    """
    Set up the Prometheus metrics endpoint in the FastAPI application.
    """
    try:
        # Include the metrics router
        app.include_router(metrics_router, tags=["Monitoring"])
        logger.info("Prometheus metrics endpoint configured at /metrics")
    except Exception as e:
        logger.error(f"Failed to set up Prometheus metrics endpoint: {str(e)}")