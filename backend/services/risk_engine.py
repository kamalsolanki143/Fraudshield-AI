"""
FraudShield AI — Risk Engine
==============================
Post-processes raw Gemini analysis output into a validated, normalised
fraud assessment result.

Responsibilities:
  • Validate the structure and types of the Gemini response.
  • Clamp / normalise the risk score to [0, 100].
  • Derive the canonical verdict from the score.
  • Produce the final result dictionary consumed by the API layer.
"""

from __future__ import annotations

import logging
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Verdict thresholds (inclusive boundaries)
# ---------------------------------------------------------------------------
_VERDICT_BANDS: List[tuple[int, int, str]] = [
    (0,  34,  "SAFE"),
    (35, 59,  "SUSPICIOUS"),
    (60, 84,  "HIGH RISK"),
    (85, 100, "CONFIRMED SCAM"),
]

_VALID_VERDICTS = {v for _, _, v in _VERDICT_BANDS}

_VALID_SCAM_TYPES = {
    "Fake KYC Scam",
    "UPI Collect Request Scam",
    "Lottery / Prize Scam",
    "Fake Customer Support Scam",
    "QR Code Tampering",
    "Suspicious UPI ID",
    "Bank Impersonation",
    "Phishing Link",
    "Refund Scam",
    "Investment / Job Scam",
    "None Detected",
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def calculate_verdict(score: int) -> str:
    """
    Map a numeric risk score to a human-readable verdict.

    Args:
        score: Integer risk score, expected in the range [0, 100].

    Returns:
        One of ``"SAFE"``, ``"SUSPICIOUS"``, ``"HIGH RISK"``,
        or ``"CONFIRMED SCAM"``.

    Raises:
        ValueError: If *score* is not an integer.
    """
    if not isinstance(score, int):
        raise ValueError(f"risk_score must be int, got {type(score).__name__}")

    # Clamp to valid range before lookup
    clamped = max(0, min(100, score))

    for low, high, verdict in _VERDICT_BANDS:
        if low <= clamped <= high:
            return verdict

    # Fallback — should never be reached given the exhaustive bands.
    return "SUSPICIOUS"


def normalize_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalise a raw Gemini response dictionary.

    Performs the following corrections:
      1. Ensures ``risk_score`` is an ``int`` clamped to [0, 100].
      2. Re-derives ``verdict`` from the normalised score (overrides any
         misclassification by Gemini).
      3. Defaults missing or empty ``scam_type`` to ``"None Detected"``.
      4. Ensures ``reasons`` is a non-empty list of strings.
      5. Provides a fallback ``action_step`` if missing.
      6. Validates ``confidence_score`` as a float clamped to [0.0, 1.0].

    Args:
        data: Raw dictionary parsed from Gemini's JSON output.

    Returns:
        A new dictionary with validated and normalised fields.

    Raises:
        ValueError: If *data* is ``None`` or not a ``dict``.
    """
    if not isinstance(data, dict):
        raise ValueError(f"Expected dict, got {type(data).__name__}")

    normalised: Dict[str, Any] = deepcopy(data)

    # --- risk_score ---
    raw_score = normalised.get("risk_score")
    try:
        score = int(raw_score)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        logger.warning("Invalid risk_score '%s' — defaulting to 50.", raw_score)
        score = 50

    score = max(0, min(100, score))
    normalised["risk_score"] = score

    # --- verdict (always re-derive from score) ---
    normalised["verdict"] = calculate_verdict(score)

    # --- scam_type (must be a recognised category) ---
    scam_type = normalised.get("scam_type")
    if not scam_type or not isinstance(scam_type, str) or not scam_type.strip():
        logger.warning("Missing or empty scam_type — defaulting to 'None Detected'.")
        normalised["scam_type"] = "None Detected"
    elif scam_type.strip() not in _VALID_SCAM_TYPES:
        logger.warning(
            "Unrecognised scam_type '%s' — defaulting to 'None Detected'. "
            "Valid types: %s",
            scam_type.strip(),
            _VALID_SCAM_TYPES,
        )
        normalised["scam_type"] = "None Detected"
    else:
        normalised["scam_type"] = scam_type.strip()

    # --- reasons ---
    reasons = normalised.get("reasons")
    if not isinstance(reasons, list) or len(reasons) == 0:
        normalised["reasons"] = ["Analysis details unavailable."]
    else:
        # Ensure every item is a non-empty string
        cleaned: List[str] = []
        for r in reasons:
            if isinstance(r, str) and r.strip():
                cleaned.append(r.strip())
        normalised["reasons"] = cleaned if cleaned else ["Analysis details unavailable."]

    # --- action_step ---
    action = normalised.get("action_step")
    if not action or not isinstance(action, str) or not action.strip():
        normalised["action_step"] = _default_action_step(score)
    else:
        normalised["action_step"] = action.strip()

    # --- confidence_score (preserve and validate if present) ---
    raw_confidence = normalised.get("confidence_score")
    if raw_confidence is not None:
        try:
            confidence = float(raw_confidence)
            # Clamp to [0.0, 1.0]
            confidence = max(0.0, min(1.0, confidence))
            normalised["confidence_score"] = round(confidence, 3)
        except (TypeError, ValueError):
            logger.warning(
                "Invalid confidence_score '%s' — removing.", raw_confidence
            )
            normalised.pop("confidence_score", None)

    return normalised


def generate_final_result(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Produce the final, API-ready fraud assessment result.

    Wraps :func:`normalize_response` and enriches the output with
    additional metadata fields useful for the frontend and database:

      • ``analysed_at`` — ISO-8601 UTC timestamp of analysis completion.
      • ``risk_level`` — colour-coded severity tag for UI rendering.
      • ``is_dangerous`` — boolean convenience flag (True if score ≥ 60).
      • ``confidence_score`` — always present; defaults to 0.8 if not
        provided by the upstream analysis.

    Args:
        data: Raw dictionary from Gemini (or a partially valid fallback).

    Returns:
        Complete, validated result dictionary.
    """
    result = normalize_response(data)

    # Enrich with metadata
    result["analysed_at"] = datetime.now(timezone.utc).isoformat()
    result["risk_level"] = _risk_level_tag(result["risk_score"])
    result["is_dangerous"] = result["risk_score"] >= 60

    # Guarantee confidence_score is always present in the final output.
    # Default to 0.8 — a realistic baseline when Gemini doesn't provide one.
    result.setdefault("confidence_score", 0.8)

    logger.info(
        "Final result: score=%d  verdict=%s  scam_type=%s  confidence=%.3f",
        result["risk_score"],
        result["verdict"],
        result["scam_type"],
        result["confidence_score"],
    )

    return result


# ---------------------------------------------------------------------------
# Utility: build a safe fallback result when Gemini fails entirely.
# ---------------------------------------------------------------------------
def build_fallback_result(error_message: Optional[str] = None) -> Dict[str, Any]:
    """
    Return a safe fallback result when analysis cannot be completed.

    This ensures the API always returns a well-formed response even when
    the upstream AI service is unavailable or returns garbage.

    Args:
        error_message: Optional human-readable error description.

    Returns:
        A result dictionary with score 50 and ``SUSPICIOUS`` verdict.
    """
    reason = error_message or "Unable to complete automated analysis. Please review manually."
    fallback_data: Dict[str, Any] = {
        "risk_score": 50,
        "verdict": "SUSPICIOUS",
        "scam_type": "None Detected",
        "reasons": [reason],
        "action_step": "Exercise caution. Verify the sender through official channels before proceeding.",
    }
    return generate_final_result(fallback_data)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _risk_level_tag(score: int) -> str:
    """Return a colour-coded tag for frontend badge rendering."""
    if score <= 34:
        return "green"
    if score <= 59:
        return "yellow"
    if score <= 84:
        return "orange"
    return "red"


def _default_action_step(score: int) -> str:
    """Generate a sensible default action when Gemini omits one."""
    if score <= 34:
        return "This appears safe. No action needed."
    if score <= 59:
        return "Proceed with caution. Verify the sender before taking any action."
    if score <= 84:
        return "Do not proceed. This looks highly suspicious — contact your bank if needed."
    return "Do NOT proceed. This is very likely a scam. Report it immediately."
