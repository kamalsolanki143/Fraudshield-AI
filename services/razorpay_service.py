"""Razorpay integration service.

Handles order creation for user subscriptions, payment signature verification
using SHA256 HMAC, and subscription plan amount lookups.
"""

import asyncio
import hashlib
import hmac
import os
from dotenv import load_dotenv
import razorpay

load_dotenv()

# Initialize Razorpay client
client = razorpay.Client(
    auth=(
        os.getenv("RAZORPAY_KEY_ID", "rzp_test_placeholder"),
        os.getenv("RAZORPAY_KEY_SECRET", "secret_placeholder"),
    )
)

PLAN_AMOUNTS = {
    "pro": 4900,       # ₹49.00 in paise
    "family": 9900,    # ₹99.00 in paise
    "business": 49900,  # ₹499.00 in paise
}


def _create_order_sync(amount_paise: int, receipt: str) -> dict:
    """Synchronous SDK execution helper to create an order."""
    data = {
        "amount": amount_paise,
        "currency": "INR",
        "receipt": receipt,
    }
    return client.order.create(data=data)


async def create_order(amount_paise: int, receipt: str) -> dict:
    """Create a new Razorpay payment order asynchronously.

    Runs the synchronous SDK call in a worker thread to keep the event loop unblocked.

    Args:
        amount_paise: The payment amount in paise.
        receipt: A unique receipt identifier string.

    Returns:
        dict: The Razorpay order dictionary.
    """
    return await asyncio.to_thread(_create_order_sync, amount_paise, receipt)


def verify_payment(order_id: str, payment_id: str, signature: str) -> bool:
    """Verify the authenticity of a completed Razorpay payment signature.

    Uses SHA256 HMAC with the secret key and performs a constant-time comparison
    to prevent timing attacks.

    Args:
        order_id: The Razorpay order ID.
        payment_id: The Razorpay payment ID.
        signature: The signature hex string sent by the client.

    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    key_secret = os.getenv("RAZORPAY_KEY_SECRET", "secret_placeholder")
    msg = f"{order_id}|{payment_id}".encode("utf-8")

    generated_signature = hmac.new(
        key_secret.encode("utf-8"),
        msg,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(generated_signature, signature)


def get_plan_amount(plan: str) -> int:
    """Get the billing amount for a given plan in paise.

    Args:
        plan: The plan name (pro, family, or business).

    Returns:
        int: The amount in paise.

    Raises:
        ValueError: If the plan name is unrecognized.
    """
    if plan not in PLAN_AMOUNTS:
        raise ValueError(f"Invalid subscription plan: '{plan}'. Supported plans are: pro, family, business.")
    return PLAN_AMOUNTS[plan]
