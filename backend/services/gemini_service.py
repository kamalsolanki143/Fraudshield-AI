"""
FraudShield AI — Gemini Vision Service
========================================
Integrates with Google's Gemini 1.5 Flash Vision API to analyse uploaded
screenshots for fraud indicators.

Responsibilities:
  • Connect to the Gemini API via ``google-generativeai`` SDK.
  • Encode and send screenshot images alongside the fraud analysis prompt.
  • Parse the structured JSON response from Gemini.
  • Retry up to ``_MAX_RETRIES`` times with progressively stricter prompts.
  • Extract and propagate a confidence score when Gemini provides one.
  • Enforce per-request timeouts to prevent hung API calls.
  • Validate response structure before returning data.
  • Translate analysis results into Hindi via a second Gemini call.
  • Return validated Python dictionaries to the calling layer.
"""

from __future__ import annotations

import asyncio
import json
import logging
import mimetypes
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import google.generativeai as genai
from google.generativeai.types import HarmBlockThreshold, HarmCategory

from backend.prompts.fraud_prompt import get_fraud_analysis_prompt, get_retry_prompt
from backend.prompts.hindi_prompt import get_hindi_translation_prompt
from backend.services.risk_engine import build_fallback_result, generate_final_result

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
_MODEL_NAME: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
_MAX_RETRIES: int = int(os.getenv("GEMINI_MAX_RETRIES", "2"))
_REQUEST_TIMEOUT_SECONDS: float = float(os.getenv("GEMINI_TIMEOUT", "30.0"))
_SUPPORTED_MIME_TYPES: Set[str] = {"image/png", "image/jpeg", "image/webp"}
_MAX_IMAGE_SIZE_MB: float = 10.0

# Required top-level keys that a valid Gemini fraud-analysis response must
# contain.  Used by ``_validate_response_structure`` to reject garbage.
_REQUIRED_RESPONSE_KEYS: Set[str] = {
    "risk_score",
    "verdict",
    "scam_type",
    "reasons",
    "action_step",
}

# Generation parameters tuned for deterministic JSON output
_GENERATION_CONFIG = genai.GenerationConfig(
    temperature=0.1,       # Near-deterministic for consistent risk scores
    top_p=0.95,
    top_k=40,
    max_output_tokens=1024,
)

# Safety settings — allow analysis of potentially harmful content since
# the screenshots may contain scam material that Gemini needs to inspect.
# Uses official SDK enums for type safety and forward compatibility.
_SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT:        HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH:       HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}


# ---------------------------------------------------------------------------
# Module-level initialisation
# ---------------------------------------------------------------------------
def _configure_api() -> None:
    """
    Configure the Gemini SDK with the API key from the environment.

    Raises:
        EnvironmentError: If ``GEMINI_API_KEY`` is not set.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY environment variable is not set. "
            "Please set it before starting the application."
        )
    genai.configure(api_key=api_key)


def _get_model() -> genai.GenerativeModel:
    """Return a configured Gemini GenerativeModel instance."""
    _configure_api()
    return genai.GenerativeModel(
        model_name=_MODEL_NAME,
        generation_config=_GENERATION_CONFIG,
        safety_settings=_SAFETY_SETTINGS,
    )


# ---------------------------------------------------------------------------
# Image helpers
# ---------------------------------------------------------------------------
def _resolve_mime_type(image_path: str) -> str:
    """
    Determine the MIME type of an image file.

    Args:
        image_path: Filesystem path to the image.

    Returns:
        A MIME type string (e.g. ``"image/png"``).

    Raises:
        ValueError: If the MIME type is unsupported.
    """
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        # Fallback based on extension
        ext = Path(image_path).suffix.lower()
        mime_map = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
        }
        mime_type = mime_map.get(ext)

    if mime_type not in _SUPPORTED_MIME_TYPES:
        raise ValueError(
            f"Unsupported image type '{mime_type}'. "
            f"Supported types: {', '.join(sorted(_SUPPORTED_MIME_TYPES))}"
        )
    return mime_type


def _load_image_as_part(image_path: str) -> Dict[str, Any]:
    """
    Read an image file and package it as a Gemini content part.

    Args:
        image_path: Absolute or relative path to the image file.

    Returns:
        A dict with ``mime_type`` and ``data`` keys suitable for the
        Gemini ``generate_content`` call.

    Raises:
        FileNotFoundError: If the image does not exist.
        ValueError:        If the file exceeds the size limit.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Enforce size limit
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > _MAX_IMAGE_SIZE_MB:
        raise ValueError(
            f"Image size ({size_mb:.1f} MB) exceeds the "
            f"{_MAX_IMAGE_SIZE_MB:.0f} MB limit."
        )

    mime_type = _resolve_mime_type(image_path)
    image_bytes = path.read_bytes()

    return {
        "mime_type": mime_type,
        "data": image_bytes,
    }


# ---------------------------------------------------------------------------
# JSON parsing helpers
# ---------------------------------------------------------------------------
def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    """
    Robustly extract a JSON object from Gemini's text response.

    Handles common issues in order of likelihood:
      1. Clean JSON — direct ``json.loads``.
      2. Markdown code fences (````json ... ````).
      3. Brace-boundary extraction (find outermost ``{…}``).
      4. Bracket-counting extraction for nested / trailing-garbage cases.
      5. Relaxed parsing — strip trailing commas, single-quote keys, etc.

    Args:
        text: Raw text output from Gemini.

    Returns:
        Parsed dictionary, or ``None`` if all strategies fail.
    """
    if not text or not text.strip():
        return None

    cleaned = text.strip()

    # --- Strategy 1: Direct parse ---
    result = _try_parse(cleaned)
    if result is not None:
        return result

    # --- Strategy 2: Strip markdown code fences ---
    fence_pattern = r"```(?:json)?\s*\n?(.*?)\n?\s*```"
    fence_match = re.search(fence_pattern, cleaned, re.DOTALL)
    if fence_match:
        result = _try_parse(fence_match.group(1).strip())
        if result is not None:
            return result

    # --- Strategy 3: Simple brace-boundary extraction ---
    brace_start = cleaned.find("{")
    brace_end = cleaned.rfind("}")
    if brace_start != -1 and brace_end > brace_start:
        result = _try_parse(cleaned[brace_start : brace_end + 1])
        if result is not None:
            return result

    # --- Strategy 4: Bracket-counting for nested objects ---
    result = _extract_json_by_brace_counting(cleaned)
    if result is not None:
        return result

    # --- Strategy 5: Relaxed cleanup (trailing commas, single quotes) ---
    result = _try_relaxed_parse(cleaned)
    if result is not None:
        return result

    return None


def _try_parse(text: str) -> Optional[Dict[str, Any]]:
    """Attempt ``json.loads`` and return the dict or ``None``."""
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, TypeError):
        pass
    return None


def _extract_json_by_brace_counting(text: str) -> Optional[Dict[str, Any]]:
    """
    Walk the string character-by-character, counting ``{`` / ``}`` nesting
    depth to isolate the first complete top-level JSON object.

    This handles cases where Gemini appends explanatory text after the
    closing brace or nests objects deeper than a simple rfind would catch.
    """
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    in_string = False
    escape_next = False

    for i in range(start, len(text)):
        char = text[i]

        if escape_next:
            escape_next = False
            continue

        if char == "\\":
            if in_string:
                escape_next = True
            continue

        if char == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return _try_parse(text[start : i + 1])

    return None


def _try_relaxed_parse(text: str) -> Optional[Dict[str, Any]]:
    """
    Apply common fixups for slightly-malformed JSON before parsing:
      • Remove trailing commas before ``}`` or ``]``.
      • Replace single-quoted keys/values with double quotes.
    """
    brace_start = text.find("{")
    brace_end = text.rfind("}")
    if brace_start == -1 or brace_end <= brace_start:
        return None

    fragment = text[brace_start : brace_end + 1]

    # Remove trailing commas  (e.g.  ``"key": "val",}``)
    fragment = re.sub(r",\s*([}\]])", r"\1", fragment)

    # Replace single quotes with double quotes (risky but last resort)
    if "'" in fragment and '"' not in fragment:
        fragment = fragment.replace("'", '"')

    return _try_parse(fragment)


# ---------------------------------------------------------------------------
# Response validation
# ---------------------------------------------------------------------------
def _validate_response_structure(data: Dict[str, Any]) -> bool:
    """
    Check that a parsed response contains all required top-level keys
    and that their types are broadly correct.

    This catches responses that are valid JSON but structurally wrong
    (e.g. Gemini returning a translation object instead of the fraud
    analysis schema).

    Args:
        data: Parsed dictionary from ``_extract_json``.

    Returns:
        ``True`` if the structure is acceptable, ``False`` otherwise.
    """
    if not isinstance(data, dict):
        return False

    # Must have at least 3 of the 5 required keys to be considered valid.
    # This tolerates Gemini occasionally omitting one optional-feeling key
    # while still rejecting completely wrong schemas.
    present_keys = _REQUIRED_RESPONSE_KEYS.intersection(data.keys())
    if len(present_keys) < 3:
        logger.warning(
            "Response missing required keys. Present: %s, Required: %s",
            present_keys,
            _REQUIRED_RESPONSE_KEYS,
        )
        return False

    # Type spot-checks
    risk_score = data.get("risk_score")
    if risk_score is not None:
        try:
            int(risk_score)
        except (TypeError, ValueError):
            logger.warning("risk_score is not numeric: %r", risk_score)
            return False

    reasons = data.get("reasons")
    if reasons is not None and not isinstance(reasons, list):
        logger.warning("reasons is not a list: %r", type(reasons).__name__)
        return False

    return True


# ---------------------------------------------------------------------------
# Confidence score helpers
# ---------------------------------------------------------------------------
def _extract_confidence_score(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    If Gemini includes a ``confidence`` or ``confidence_score`` field,
    normalise it into a ``confidence_score`` float in [0.0, 1.0] and
    attach it to the result.

    If no confidence field is present, a heuristic score is derived
    from the completeness of the response.

    Args:
        data: The parsed (but not yet finalised) response dict.

    Returns:
        The same dict, enriched with a ``confidence_score`` key.
    """
    # Check for Gemini-provided confidence
    raw = data.get("confidence") or data.get("confidence_score")
    if raw is not None:
        try:
            score = float(raw)
            # Normalise percentages (e.g. 85) to [0, 1]
            if score > 1.0:
                score = score / 100.0
            data["confidence_score"] = round(max(0.0, min(1.0, score)), 3)
            return data
        except (TypeError, ValueError):
            pass

    # Heuristic: derive confidence from response completeness
    present = sum(1 for k in _REQUIRED_RESPONSE_KEYS if data.get(k))
    reasons = data.get("reasons", [])
    reason_bonus = min(len(reasons), 3) * 0.05  # Up to 0.15 for 3+ reasons
    completeness = (present / len(_REQUIRED_RESPONSE_KEYS)) * 0.85 + reason_bonus
    data["confidence_score"] = round(max(0.0, min(1.0, completeness)), 3)

    return data


# ---------------------------------------------------------------------------
# Timeout-wrapped Gemini call
# ---------------------------------------------------------------------------
async def _call_gemini_with_timeout(
    model: genai.GenerativeModel,
    contents: list,
    timeout: float = _REQUEST_TIMEOUT_SECONDS,
) -> Optional[str]:
    """
    Send a request to Gemini with an ``asyncio.wait_for`` timeout.

    Args:
        model:    Configured ``GenerativeModel`` instance.
        contents: The content parts list (image + prompt, or text-only).
        timeout:  Maximum seconds to wait before raising ``TimeoutError``.

    Returns:
        The response text, or ``None`` if the response is empty or blocked.

    Raises:
        asyncio.TimeoutError: If the request exceeds *timeout* seconds.
    """
    response = await asyncio.wait_for(
        model.generate_content_async(contents=contents),
        timeout=timeout,
    )

    if not response:
        return None

    # Handle safety-blocked responses
    try:
        if response.prompt_feedback and response.prompt_feedback.block_reason:
            logger.warning(
                "Gemini blocked the request: %s",
                response.prompt_feedback.block_reason,
            )
            return None
    except (AttributeError, ValueError):
        pass

    try:
        return response.text
    except (AttributeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Core analysis function
# ---------------------------------------------------------------------------
async def analyze_screenshot(image_path: str) -> Dict[str, Any]:
    """
    Analyse a screenshot for fraud indicators using Gemini Vision.

    Sends the image with the fraud analysis prompt, retries up to
    ``_MAX_RETRIES`` times on parse / validation failure (alternating
    between the primary and a stricter retry prompt), and returns a
    validated result dictionary.

    Args:
        image_path: Path to the screenshot file (PNG, JPG, JPEG, or WebP).

    Returns:
        A validated and normalised result dictionary produced by
        :func:`~backend.services.risk_engine.generate_final_result`,
        enriched with a ``confidence_score`` field.
        On unrecoverable failure, returns a safe fallback result.
    """
    try:
        model = _get_model()
        image_part = _load_image_as_part(image_path)
    except FileNotFoundError as exc:
        logger.error("Image file error: %s", exc)
        return build_fallback_result(f"Image file error: {exc}")
    except ValueError as exc:
        logger.error("Validation error: %s", exc)
        return build_fallback_result(f"Validation error: {exc}")
    except EnvironmentError as exc:
        logger.error("Configuration error: %s", exc)
        return build_fallback_result(f"Configuration error: {exc}")

    # Build the prompt sequence: first attempt uses the primary prompt,
    # subsequent retries use the stricter retry prompt.
    primary_prompt = get_fraud_analysis_prompt()
    retry_prompt = get_retry_prompt()

    last_raw_text: Optional[str] = None

    for attempt in range(1, _MAX_RETRIES + 1):
        prompt = primary_prompt if attempt == 1 else retry_prompt
        attempt_label = f"attempt {attempt}/{_MAX_RETRIES}"

        try:
            logger.info(
                "Sending screenshot to Gemini (%s): %s",
                attempt_label,
                image_path,
            )

            raw_text = await _call_gemini_with_timeout(
                model=model,
                contents=[image_part, prompt],
            )

            if not raw_text:
                logger.warning(
                    "Gemini returned empty/blocked response on %s.",
                    attempt_label,
                )
                last_raw_text = None
                continue

            last_raw_text = raw_text

            # Parse JSON from the response
            parsed = _extract_json(raw_text)
            if parsed is None:
                logger.warning(
                    "Failed to extract JSON on %s. Raw (first 300 chars): %.300s",
                    attempt_label,
                    raw_text,
                )
                continue

            # Validate structural integrity
            if not _validate_response_structure(parsed):
                logger.warning(
                    "Response failed structural validation on %s.",
                    attempt_label,
                )
                continue

            # Enrich with confidence score
            parsed = _extract_confidence_score(parsed)

            # Validate and normalise through the risk engine
            logger.info(
                "Successfully parsed Gemini response on %s.", attempt_label
            )
            return generate_final_result(parsed)

        except asyncio.TimeoutError:
            logger.error(
                "Gemini request timed out after %.1fs on %s.",
                _REQUEST_TIMEOUT_SECONDS,
                attempt_label,
            )
            continue

        except Exception as exc:
            logger.exception(
                "Unexpected error on %s: %s", attempt_label, exc
            )
            # Only continue retrying for transient errors
            if attempt < _MAX_RETRIES:
                continue
            return build_fallback_result(
                f"Analysis failed due to an unexpected error: "
                f"{type(exc).__name__}"
            )

    # All retries exhausted
    detail = ""
    if last_raw_text:
        detail = f" Last raw response (first 200 chars): {last_raw_text[:200]}"
    logger.error(
        "Could not obtain valid Gemini response after %d attempts.%s",
        _MAX_RETRIES,
        detail,
    )
    return build_fallback_result(
        "AI analysis returned an unreadable response after multiple "
        "attempts. Manual review recommended."
    )


# ---------------------------------------------------------------------------
# Hindi translation function
# ---------------------------------------------------------------------------
async def translate_to_hindi(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Translate an English fraud analysis result into conversational Hindi.

    Uses a second Gemini call with the Hindi translation prompt.  On
    failure, returns pre-mapped Hindi labels as a minimal fallback.

    Args:
        result: A normalised result dictionary (output of
                :func:`analyze_screenshot` or
                :func:`~backend.services.risk_engine.generate_final_result`).

    Returns:
        A dictionary containing Hindi translations of the analysis fields.
        On failure, returns a minimal translation using static label maps.
    """
    from backend.prompts.hindi_prompt import (
        get_instant_hindi_scam_type,
        get_instant_hindi_verdict,
    )

    try:
        model = _get_model()
        prompt = get_hindi_translation_prompt(
            risk_score=result.get("risk_score", 50),
            verdict=result.get("verdict", "SUSPICIOUS"),
            scam_type=result.get("scam_type", "None Detected"),
            reasons=result.get("reasons", []),
            action_step=result.get("action_step", ""),
        )

        logger.info("Requesting Hindi translation from Gemini.")

        raw_text = await _call_gemini_with_timeout(
            model=model,
            contents=[prompt],
            timeout=_REQUEST_TIMEOUT_SECONDS,
        )

        if raw_text:
            parsed = _extract_json(raw_text)
            if parsed:
                return parsed

        logger.warning(
            "Hindi translation failed — using static fallback labels."
        )

    except asyncio.TimeoutError:
        logger.error(
            "Hindi translation timed out after %.1fs.",
            _REQUEST_TIMEOUT_SECONDS,
        )

    except Exception:
        logger.exception("Error during Hindi translation.")

    # Minimal fallback using pre-built label maps
    score = result.get("risk_score", 50)
    return {
        "risk_score_hindi": f"खतरे का स्तर: {score}/100",
        "verdict_hindi": get_instant_hindi_verdict(
            result.get("verdict", "SUSPICIOUS")
        ),
        "scam_type_hindi": get_instant_hindi_scam_type(
            result.get("scam_type", "None Detected")
        ),
        "reasons_hindi": result.get(
            "reasons", ["विश्लेषण उपलब्ध नहीं है।"]
        ),
        "action_step_hindi": (
            "कृपया सावधानी बरतें और किसी भी भुगतान से पहले पुष्टि करें।"
        ),
        "summary_hindi": _get_dynamic_hindi_summary(score),
    }


def _get_dynamic_hindi_summary(score: int) -> str:
    """
    Return a risk-appropriate Hindi summary for the fallback path.

    Uses the same score thresholds as the risk engine verdicts:
      0–34  → SAFE, 35–59 → SUSPICIOUS, 60–84 → HIGH RISK, 85–100 → CONFIRMED SCAM.
    """
    if score <= 34:
        return "यह स्क्रीनशॉट सुरक्षित दिखता है। चिंता की कोई बात नहीं है। ✅"
    if score <= 59:
        return "यह स्क्रीनशॉट थोड़ा संदिग्ध लग रहा है। कृपया सतर्क रहें। ⚠️"
    if score <= 84:
        return "यह स्क्रीनशॉट बहुत खतरनाक लग रहा है। कृपया आगे न बढ़ें और सावधानी बरतें। 🔴"
    return "यह स्क्रीनशॉट पक्का धोखाधड़ी है! किसी भी हालत में आगे न बढ़ें और तुरंत रिपोर्ट करें। 🚨"
