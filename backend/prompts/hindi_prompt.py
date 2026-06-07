"""
FraudShield AI — Hindi Translation Prompts
============================================
Converts English fraud analysis results into simple, conversational Hindi
that is easy for non-technical Indian users to understand.
"""

from __future__ import annotations

from typing import Dict, List


# ---------------------------------------------------------------------------
# Gemini prompt for translating the full analysis result into Hindi.
# ---------------------------------------------------------------------------
HINDI_TRANSLATION_PROMPT: str = """
You are a friendly Hindi translator for a fraud-detection app used by
everyday Indian users — many of whom are not tech-savvy.

## Your Task
Translate the following fraud analysis result into **simple, conversational
Hindi** (Hinglish is acceptable where it improves clarity).

## Translation Rules
1. **No technical jargon** — replace terms like "phishing", "QR tampering",
   or "UPI collect request" with plain-language Hindi equivalents that a
   common user would understand.
2. **Keep it short and clear** — each translated reason should be one
   concise sentence.
3. **Preserve the original meaning** — do not add, remove, or exaggerate
   any information.
4. **Use a caring, supportive tone** — the user may be worried; reassure
   them where appropriate.
5. **Use Devanagari script** for Hindi portions.

## Input (English)
Risk Score: {risk_score}
Verdict: {verdict}
Scam Type: {scam_type}
Reasons:
{reasons}
Recommended Action: {action_step}

## Required Output Format
Return ONLY a valid JSON object with this structure:

{{
  "risk_score_hindi": "<score in Hindi, e.g. 'खतरे का स्तर: 85/100'>",
  "verdict_hindi": "<verdict in Hindi>",
  "scam_type_hindi": "<scam type in Hindi>",
  "reasons_hindi": [
    "<reason 1 in Hindi>",
    "<reason 2 in Hindi>"
  ],
  "action_step_hindi": "<recommended action in Hindi>",
  "summary_hindi": "<a 1–2 sentence conversational summary in Hindi>"
}}

Return ONLY the JSON object.  No markdown, no explanation.
""".strip()


# ---------------------------------------------------------------------------
# Pre-built Hindi verdict labels — used for instant UI rendering before the
# full Gemini translation completes (avoids an extra API call for simple
# labels).
# ---------------------------------------------------------------------------
VERDICT_HINDI_MAP: Dict[str, str] = {
    "SAFE":           "सुरक्षित ✅",
    "SUSPICIOUS":     "संदिग्ध ⚠️",
    "HIGH RISK":      "बहुत खतरनाक 🔴",
    "CONFIRMED SCAM": "पक्का धोखाधड़ी 🚨",
}

SCAM_TYPE_HINDI_MAP: Dict[str, str] = {
    "Fake KYC Scam":              "नकली KYC स्कैम",
    "UPI Collect Request Scam":   "UPI कलेक्ट रिक्वेस्ट स्कैम",
    "Lottery / Prize Scam":       "लॉटरी / इनाम का झांसा",
    "Fake Customer Support Scam": "नकली कस्टमर सपोर्ट स्कैम",
    "QR Code Tampering":          "QR कोड में छेड़छाड़",
    "Suspicious UPI ID":          "संदिग्ध UPI आईडी",
    "Bank Impersonation":         "बैंक की नकल",
    "Phishing Link":              "फिशिंग लिंक (जाली वेबसाइट)",
    "Refund Scam":                "रिफंड का झांसा",
    "Investment / Job Scam":      "निवेश / नौकरी का झांसा",
    "None Detected":              "कोई खतरा नहीं मिला",
}


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------
def get_hindi_translation_prompt(
    risk_score: int,
    verdict: str,
    scam_type: str,
    reasons: List[str],
    action_step: str,
) -> str:
    """
    Build the Hindi translation prompt populated with analysis results.

    Args:
        risk_score:  Numeric risk score (0-100).
        verdict:     English verdict string.
        scam_type:   Detected scam category.
        reasons:     List of English reason strings.
        action_step: English recommended action.

    Returns:
        Formatted prompt string ready to send to Gemini.
    """
    formatted_reasons = "\n".join(f"- {r}" for r in reasons)

    return HINDI_TRANSLATION_PROMPT.format(
        risk_score=risk_score,
        verdict=verdict,
        scam_type=scam_type,
        reasons=formatted_reasons,
        action_step=action_step,
    )


def get_instant_hindi_verdict(verdict: str) -> str:
    """
    Return a pre-translated Hindi verdict label for instant UI feedback.

    Falls back to the English verdict if no mapping exists.
    """
    return VERDICT_HINDI_MAP.get(verdict, verdict)


def get_instant_hindi_scam_type(scam_type: str) -> str:
    """
    Return a pre-translated Hindi scam-type label for instant UI feedback.

    Falls back to the English scam type if no mapping exists.
    """
    return SCAM_TYPE_HINDI_MAP.get(scam_type, scam_type)
