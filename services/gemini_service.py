"""Gemini AI analysis service stub.

Contains stubs for Gemini prompt analysis to be completed by teammate Kamal.
"""


async def analyze_image(image_url: str, user_level: str) -> dict:
    """Analyze a screenshot image using Gemini.

    Currently a stub returning a mock high-risk verdict payload.

    Args:
        image_url: The secure Cloudinary URL of the uploaded image.
        user_level: The user's Fraud IQ level ('novice', 'aware', 'vigilant').

    Returns:
        dict: A dictionary containing verdict, confidence score, scam type,
              and explanation text in English and Hindi.
    """
    # This is a stub filled by Kamal.
    return {
        "verdict": "high_risk",
        "confidence_score": 87,
        "scam_type": "UPI Refund Scam",
        "explanation_en": "This appears to be a UPI refund scam. [STUB]",
        "explanation_hi": "यह एक UPI रिफंड स्कैम लगता है। [STUB]",
        "recommended_action": "Do not proceed with this payment.",
    }
