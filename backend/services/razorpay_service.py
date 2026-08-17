"""
FraudShield AI — Razorpay Integration Service
================================================
Handles Razorpay order creation, HMAC-SHA256 payment signature verification,
and subscription plan pricing lookups.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import logging
import os

import razorpay
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Initialise Razorpay client
client = razorpay.Client(
    auth=(
        os.getenv("RAZORPAY_KEY_ID", "rzp_test_placeholder"),
        os.getenv("RAZORPAY_KEY_SECRET", "secret_placeholder"),
    )
)

PLAN_AMOUNTS: dict[str, int] = {
    "pro": 4900,       # ₹49.00 in paise
    "family": 9900,    # ₹99.00 in paise
    "business": 49900,  # ₹499.00 in paise
}


def _create_order_sync(amount_paise: int, receipt: str) -> dict:
    """Synchronous SDK helper to create a Razorpay order."""
    data = {
        "amount": amount_paise,
        "currency": "INR",
        "receipt": receipt,
    }
    return client.order.create(data=data)


async def create_order(amount_paise: int, receipt: str) -> dict:
    """Create a Razorpay payment order asynchronously.

    Offloads the synchronous SDK call to a worker thread.

    Args:
        amount_paise: Payment amount in paise.
        receipt:      Unique receipt identifier string.

    Returns:
        The Razorpay order dictionary.
    """
    order = await asyncio.to_thread(_create_order_sync, amount_paise, receipt)
    logger.info("Created Razorpay order: %s", order.get("id"))
    return order


def verify_payment(order_id: str, payment_id: str, signature: str) -> bool:
    """Verify a Razorpay payment signature using HMAC-SHA256.

    Performs constant-time comparison to prevent timing attacks.

    Args:
        order_id:   Razorpay order ID.
        payment_id: Razorpay payment ID.
        signature:  Hex signature string from the client.

    Returns:
        ``True`` if the signature is valid, ``False`` otherwise.
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
    """Get the billing amount for a plan in paise.

    Args:
        plan: Plan name (``pro``, ``family``, or ``business``).

    Returns:
        Amount in paise.

    Raises:
        ValueError: If the plan name is unrecognised.
    """
    if plan not in PLAN_AMOUNTS:
        raise ValueError(
            f"Invalid subscription plan: '{plan}'. "
            f"Supported plans are: {', '.join(PLAN_AMOUNTS.keys())}"
        )
    return PLAN_AMOUNTS[plan]
