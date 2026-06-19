"""MongoDB connection module using Motor async driver.

Sets up connection client and exposes helper functions to get database access,
as well as establishing indexes on collections for optimized querying.
"""

import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

client = None
db = None


async def connect_db() -> None:
    """Connect to MongoDB Atlas and initialize collection indices.

    Creates unique and indexed constraints on the users, analyses,
    fraud_database, and fraud_reports collections.
    """
    global client, db
    uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME", "fraudshield")
    client = AsyncIOMotorClient(uri)
    db = client[db_name]

    # Create indexes as required
    await db.users.create_index("uid", unique=True)
    await db.users.create_index("phone", unique=True)
    await db.users.create_index("referral_code", unique=True)
    await db.analyses.create_index("user_uid")
    await db.analyses.create_index([("created_at", -1)])
    await db.fraud_database.create_index("entity_value", unique=True)
    await db.fraud_reports.create_index("entity_value")
    print("✅ MongoDB connected")


async def close_db() -> None:
    """Close the MongoDB connection client."""
    global client
    if client:
        client.close()
        print("🔌 MongoDB disconnected")


def get_db():
    """Return the active MongoDB database instance.

    Returns:
        AsyncIOMotorDatabase: The connected database object.
    """
    return db
