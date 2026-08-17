"""
FraudShield AI — Fraud Analysis Orchestrator
===============================================
Bridges the API layer to the Gemini Vision AI service and Risk Engine.

Orchestration flow::

    File bytes → temp file → Gemini analyze_screenshot() →
    Risk Engine generate_final_result() → translate_to_hindi() →
    clean up → return combined result dict

This module DOES NOT duplicate Gemini logic — it simply calls the
existing ``backend.services.gemini_service`` and
``backend.services.risk_engine`` modules.
"""

from __future__ import annotations

import logging
import os
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict

from backend.services.gemini_service import analyze_screenshot, translate_to_hindi

logger = logging.getLogger(__name__)


async def analyze_fraud_screenshot(
    file_bytes: bytes,
    original_filename: str,
) -> Dict[str, Any]:
    """Run full fraud analysis on an uploaded screenshot.

    Saves the uploaded bytes to a temporary file, delegates analysis to
    the Gemini Vision service, requests a Hindi translation, and cleans
    up the temporary file.

    Args:
        file_bytes:        Raw bytes of the uploaded image file.
        original_filename: The original filename for MIME-type resolution.

    Returns:
        A complete result dictionary containing both English and Hindi
        analysis results, ready for API serialisation and database storage.
    """
    # Determine file extension from the original filename
    ext = Path(original_filename).suffix.lower() or ".png"
    temp_path: str | None = None

    try:
        # Write to a temporary file that the Gemini service can read
        temp_dir = os.path.join(tempfile.gettempdir(), "fraudshield_uploads")
        os.makedirs(temp_dir, exist_ok=True)

        temp_filename = f"{uuid.uuid4().hex}{ext}"
        temp_path = os.path.join(temp_dir, temp_filename)

        with open(temp_path, "wb") as f:
            f.write(file_bytes)

        logger.info(
            "Saved upload to temp file: %s (%d bytes)",
            temp_path,
            len(file_bytes),
        )

        # ---- Step 1: Gemini Vision Analysis ----
        analysis_result = await analyze_screenshot(temp_path)

        logger.info(
            "Gemini analysis complete: score=%s  verdict=%s",
            analysis_result.get("risk_score"),
            analysis_result.get("verdict"),
        )

        # ---- Step 2: Hindi Translation ----
        try:
            hindi_result = await translate_to_hindi(analysis_result)
            analysis_result["hindi"] = hindi_result
            analysis_result["explanation_hi"] = hindi_result.get(
                "summary_hindi", ""
            )
        except Exception as exc:
            logger.warning("Hindi translation failed: %s", exc)
            analysis_result["hindi"] = {}
            analysis_result["explanation_hi"] = ""

        # Build English explanation from reasons
        reasons = analysis_result.get("reasons", [])
        analysis_result["explanation_en"] = " ".join(reasons) if reasons else ""

        return analysis_result

    finally:
        # ---- Clean up temporary file ----
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
                logger.debug("Cleaned up temp file: %s", temp_path)
            except OSError as exc:
                logger.warning("Failed to delete temp file %s: %s", temp_path, exc)
