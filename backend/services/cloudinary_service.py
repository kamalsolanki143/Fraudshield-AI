"""
FraudShield AI — Cloudinary Integration Service
==================================================
Handles secure image uploads and deletions on Cloudinary for
screenshot evidence storage.
"""

from __future__ import annotations

import asyncio
import logging
import os
import uuid

import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Configure Cloudinary on import
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)


def _upload_sync(file_bytes: bytes, public_id: str) -> dict:
    """Synchronous upload execution helper."""
    return cloudinary.uploader.upload(
        file_bytes,
        public_id=public_id,
        folder="fraudshield/screenshots/",
    )


def _delete_sync(public_id: str) -> dict:
    """Synchronous destroy execution helper."""
    return cloudinary.uploader.destroy(public_id)


async def upload_image(file_bytes: bytes, original_filename: str) -> dict:
    """Upload image bytes to Cloudinary asynchronously.

    Generates a UUID-based ``public_id`` and uploads to the
    ``fraudshield/screenshots/`` folder.

    Args:
        file_bytes:        The raw bytes of the image file.
        original_filename: The original filename of the uploaded file.

    Returns:
        A dict with ``url`` (secure URL) and ``public_id`` keys.
    """
    name_base = os.path.splitext(os.path.basename(original_filename))[0]
    clean_name = "".join(c for c in name_base if c.isalnum() or c in ("-", "_"))
    public_id = f"{clean_name}_{uuid.uuid4().hex}"

    result = await asyncio.to_thread(_upload_sync, file_bytes, public_id)

    logger.info("Uploaded image to Cloudinary: %s", result.get("public_id"))

    return {
        "url": result.get("secure_url"),
        "public_id": result.get("public_id"),
    }


async def delete_image(public_id: str) -> bool:
    """Delete an image from Cloudinary by its public ID.

    Args:
        public_id: The Cloudinary public ID of the image.

    Returns:
        ``True`` if the deletion was successful, ``False`` otherwise.
    """
    result = await asyncio.to_thread(_delete_sync, public_id)
    success = result.get("result") == "ok"
    if success:
        logger.info("Deleted image from Cloudinary: %s", public_id)
    else:
        logger.warning("Cloudinary deletion returned: %s", result)
    return success
