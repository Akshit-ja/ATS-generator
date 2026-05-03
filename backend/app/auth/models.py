"""Compatibility layer.

The canonical SQLAlchemy models live in app.db.models.
This module re-exports User so older imports/tests using app.auth.models keep working
without defining a second SQLAlchemy mapper for the same table.
"""

from ..db.models import User  # noqa: F401
