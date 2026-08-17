"""
FraudShield AI — MongoDB Connection Manager
=============================================
Async Motor driver singleton with connection pooling, automatic index
creation, and graceful shutdown support.

Usage::

    from backend.database.mongo import get_db, connect_db, close_db
"""

from __future__ import annotations

import logging
import os
from typing import Optional

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level singleton state
# ---------------------------------------------------------------------------
_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
async def connect_db() -> None:
    """Connect to MongoDB Atlas and initialise collection indexes.

    Creates unique and compound indexes on the ``users``, ``analyses``,
    ``fraud_database``, ``fraud_reports``, ``alerts``, and ``subscriptions``
    collections to guarantee query performance and data integrity.

    Raises:
        RuntimeError: If ``MONGODB_URI`` is not configured.
    """
    global _client, _db

    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError(
            "MONGODB_URI environment variable is not set. "
            "Please configure it before starting the application."
        )

    db_name = os.getenv("MONGODB_DB_NAME", "fraudshield")

    _client = AsyncIOMotorClient(
        uri,
        maxPoolSize=50,
        minPoolSize=5,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000,
    )
    _db = _client[db_name]

    # ---- Index creation ----
    # Users
    await _db.users.create_index("uid", unique=True)
    await _db.users.create_index("phone", unique=True)
    await _db.users.create_index("referral_code", unique=True)

    # Analyses (fraud scan history)
    await _db.analyses.create_index("user_uid")
    await _db.analyses.create_index([("created_at", -1)])
    await _db.analyses.create_index("analysis_id", unique=True)

    # Community fraud database (lookup table)
    await _db.fraud_database.create_index("entity_value", unique=True)

    # Community fraud reports
    await _db.fraud_reports.create_index("entity_value")
    await _db.fraud_reports.create_index("reporter_uid")
    await _db.fraud_reports.create_index("report_id", unique=True)

    # Alerts
    await _db.alerts.create_index("alert_id", unique=True)
    await _db.alerts.create_index([("created_at", -1)])

    # Subscriptions
    await _db.subscriptions.create_index("uid", unique=True)

    logger.info("✅ MongoDB connected to database '%s'", db_name)


async def close_db() -> None:
    """Gracefully close the MongoDB client connection."""
    global _client, _db
    if _client is not None:
        _client.close()
        _client = None
        _db = None
        logger.info("🔌 MongoDB disconnected")


def get_db() -> AsyncIOMotorDatabase:
    """Return the active MongoDB database instance.

    Returns:
        The connected ``AsyncIOMotorDatabase`` object.

    Raises:
        RuntimeError: If called before :func:`connect_db`.
    """
    if _db is None:
        raise RuntimeError(
            "Database not initialised. Call connect_db() during application startup."
        )
    return _db
