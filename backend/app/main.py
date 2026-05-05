from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import resume, job, generate, validate, documents
from .auth.routes import router as auth_router, users_router
from .routers import admin, budget, interview
from .database import engine, Base
from .core.telemetry import setup_telemetry, instrument_app
from .core.prometheus_config import setup_prometheus_endpoint
import redis
import os

# Initialize OpenTelemetry
setup_telemetry()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Resume AI Generator API",
    description="API for generating AI-powered resumes",
    version="0.1.0",
)

# Configure CORS
from .core.config import settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if "," in settings.CORS_ORIGINS else [settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include the resume optimization router FIRST (to take precedence)
from .routers import resume_optimization
app.include_router(resume_optimization.router)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(resume.router)
app.include_router(job.router)
app.include_router(generate.router)
app.include_router(validate.router)
app.include_router(documents.router)
app.include_router(admin.router)
app.include_router(budget.router)
app.include_router(interview.router)

# Import and include the new resume generation router
from .routers import resume_generation
app.include_router(resume_generation.router)

# Initialize Redis client for instrumentation
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(redis_url)

# Instrument FastAPI app and its dependencies
instrument_app(app, db_engine=engine, redis_client=redis_client)

# Set up Prometheus metrics endpoint
setup_prometheus_endpoint(app)

@app.get("/")
async def root():
    return {"message": "Welcome to Resume AI Generator API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}