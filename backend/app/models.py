"""Compatibility module for model imports.

This project defines SQLAlchemy models under app.db.models.
Some routers/services expect to import from app.models.

We re-export the ORM classes here so `from app.models import X` works.
"""

from .db.models import *  # noqa: F401,F403
