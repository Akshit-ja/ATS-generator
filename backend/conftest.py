import os

# Fallback to SQLite for local test runs when no DATABASE_URL is provided
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("DISABLE_TELEMETRY", "true")
