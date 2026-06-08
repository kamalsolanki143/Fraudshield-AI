"""Cloudinary integration service.

Handles secure image uploads to Cloudinary for screenshotted payment proofs
and suspicious QR codes, alongside utilities for image deletion.
"""

import asyncio
import os
import uuid
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

# Configure Cloudinary immediately on import
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

    Generates a UUID-based public_id and uploads the file to the
    'fraudshield/screenshots/' folder.

    Args:
        file_bytes: The raw bytes of the image file.
        original_filename: The original filename of the uploaded file.

    Returns:
        dict: A dictionary containing 'url' and 'public_id' of the uploaded image.
    """
    # Create a unique filename prefixing the original name base
    name_base = os.path.splitext(os.path.basename(original_filename))[0]
    # Clean up name base to be alphanumeric plus dashes/underscores
    clean_name = "".join(c for c in name_base if c.isalnum() or c in ("-", "_"))
    public_id = f"{clean_name}_{uuid.uuid4().hex}"

    # Delegate synchronous upload to worker thread
    result = await asyncio.to_thread(_upload_sync, file_bytes, public_id)

    return {
        "url": result.get("secure_url"),
        "public_id": result.get("public_id"),
    }


async def delete_image(public_id: str) -> bool:
    """Delete an image from Cloudinary asynchronously by its public ID.

    Args:
        public_id: The public ID of the image to destroy.

    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    # Delegate synchronous destroy to worker thread
    result = await asyncio.to_thread(_delete_sync, public_id)
    return result.get("result") == "ok"
