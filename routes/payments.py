"""Subscription payments and Razorpay callback API router.

Handles order generation, signature verification, plan status retrieval,
and subscription cancellation.
"""

from datetime import datetime, timedelta
import os
from fastapi import APIRouter, Depends, HTTPException, status

from database.mongodb import get_db
from middleware.auth_middleware import get_current_user
from models.subscription import OrderCreate, OrderResponse, PaymentVerify, SubscriptionStatus
from services.razorpay_service import create_order, get_plan_amount, verify_payment

router = APIRouter()


@router.post(
    "/create-order",
    status_code=status.HTTP_201_CREATED,
    summary="Create a Razorpay order for subscription",
)
async def create_payment_order(
    payload: OrderCreate,
    current_user: dict = Depends(get_current_user),
):
    """Generate a Razorpay order to upgrade the user's subscription plan.

    Registers a pending subscription log in the database.
    """
    db = get_db()
    now = datetime.utcnow()

    # Get paise amount for requested plan
    try:
        amount_paise = get_plan_amount(payload.plan)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": str(e),
                "code": "INVALID_PLAN",
            },
        )

    # Generate unique receipt ID
    receipt_id = f"rcpt_{current_user['uid']}_{int(now.timestamp())}"

    # Call Razorpay SDK (non-blocking)
    try:
        order = await create_order(amount_paise, receipt_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "success": False,
                "error": f"Payment gateway communication failure: {str(e)}",
                "code": "PAYMENT_GATEWAY_ERROR",
            },
        )

    razorpay_order_id = order.get("id")

    # Upsert a pending subscription document to track the plan purchase
    await db.subscriptions.update_one(
        {"uid": current_user["uid"]},
        {
            "$set": {
                "uid": current_user["uid"],
                "plan": payload.plan,
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": "",
                "razorpay_signature": "",
                "status": "pending",
                "started_at": now,
                "expires_at": now,  # placeholder until activation
            }
        },
        upsert=True,
    )

    response_data = OrderResponse(
        razorpay_order_id=razorpay_order_id,
        amount=order.get("amount", amount_paise),
        currency=order.get("currency", "INR"),
        key_id=os.getenv("RAZORPAY_KEY_ID", "your-razorpay-key-id"),
    )

    return {
        "success": True,
        "data": response_data.model_dump(),
        "message": "Payment order generated successfully.",
    }


@router.post(
    "/verify",
    status_code=status.HTTP_200_OK,
    summary="Verify payment signature and activate plan",
)
async def verify_subscription_payment(
    payload: PaymentVerify,
    current_user: dict = Depends(get_current_user),
):
    """Verify payment webhook/callback signatures.

    Upgrades user account privileges and marks their subscription active on success.
    """
    db = get_db()
    now = datetime.utcnow()

    # Verify signature
    is_valid = verify_payment(
        order_id=payload.razorpay_order_id,
        payment_id=payload.razorpay_payment_id,
        signature=payload.razorpay_signature,
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "Payment verification failed. Invalid signature.",
                "code": "INVALID_SIGNATURE",
            },
        )

    # Fetch corresponding subscription log
    subscription = await db.subscriptions.find_one({"razorpay_order_id": payload.razorpay_order_id})
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": "Associated subscription order record not found.",
                "code": "ORDER_NOT_FOUND",
            },
        )

    expires_at = now + timedelta(days=30)
    purchased_plan = subscription.get("plan", "free")

    # Update subscription record
    await db.subscriptions.update_one(
        {"razorpay_order_id": payload.razorpay_order_id},
        {
            "$set": {
                "razorpay_payment_id": payload.razorpay_payment_id,
                "razorpay_signature": payload.razorpay_signature,
                "status": "active",
                "started_at": now,
                "expires_at": expires_at,
            }
        },
    )

    # Update user properties: set active plan and unlock infinite analyses limit (999999)
    await db.users.update_one(
        {"uid": current_user["uid"]},
        {
            "$set": {
                "plan": purchased_plan,
                "analyses_limit": 999999,  # Infinite analyses for paid tiers
                "updated_at": now,
            }
        },
    )

    return {
        "success": True,
        "data": {
            "plan": purchased_plan,
            "expires_at": expires_at.isoformat(),
        },
        "message": "Payment verified and subscription activated successfully.",
    }


@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    summary="Check subscription status",
)
async def get_subscription_status(current_user: dict = Depends(get_current_user)):
    """Retrieve the current user's active billing subscription profile."""
    db = get_db()

    subscription = await db.subscriptions.find_one({"uid": current_user["uid"]})
    if not subscription or subscription.get("status") == "pending":
        # Return fallback free tier status
        return {
            "success": True,
            "data": {
                "plan": "free",
                "status": "expired",
                "started_at": datetime.utcnow().isoformat(),
                "expires_at": datetime.utcnow().isoformat(),
            },
            "message": "No active premium subscription found.",
        }

    # Format datetime outputs to ISO strings
    started_at = subscription.get("started_at")
    expires_at = subscription.get("expires_at")
    if isinstance(started_at, datetime):
        started_at = started_at.isoformat()
    if isinstance(expires_at, datetime):
        expires_at = expires_at.isoformat()

    response_data = SubscriptionStatus(
        plan=subscription.get("plan", "free"),
        status=subscription.get("status", "expired"),
        started_at=started_at,
        expires_at=expires_at,
    )

    return {
        "success": True,
        "data": response_data.model_dump(),
        "message": "Subscription status retrieved successfully.",
    }


@router.post(
    "/cancel",
    status_code=status.HTTP_200_OK,
    summary="Cancel active subscription",
)
async def cancel_subscription(current_user: dict = Depends(get_current_user)):
    """Cancel the active billing subscription.

    Downgrades privileges immediately back to free tier.
    """
    db = get_db()
    now = datetime.utcnow()

    subscription = await db.subscriptions.find_one({"uid": current_user["uid"]})
    if not subscription or subscription.get("status") not in ("active", "cancelled"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "No active subscription found to cancel.",
                "code": "NO_ACTIVE_SUBSCRIPTION",
            },
        )

    # Set status to cancelled
    await db.subscriptions.update_one(
        {"uid": current_user["uid"]},
        {"$set": {"status": "cancelled", "expires_at": now}},
    )

    # Reset user plan properties back to free
    await db.users.update_one(
        {"uid": current_user["uid"]},
        {
            "$set": {
                "plan": "free",
                "analyses_limit": 5,
                "updated_at": now,
            }
        },
    )

    return {
        "success": True,
        "data": None,
        "message": "Subscription cancelled successfully. Downgraded to free tier.",
    }
