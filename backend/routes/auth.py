"""
FraudShield AI — Authentication Router
=========================================
Handles user registration, login, profile retrieval, and profile updates.
All endpoints return the standard ``{success, data, message}`` JSON envelope.
"""

from __future__ import annotations

import logging
import random
import string
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from backend.database.mongo import get_db
from backend.middleware.auth_middleware import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    hash_password,
    verify_password,
)
from backend.models.user import (
    TokenResponse,
    UserLogin,
    UserProfile,
    UserRegister,
    UserUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _generate_referral_code() -> str:
    """Generate a random 8-character uppercase alphanumeric referral code."""
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=8))


async def _ensure_unique_referral_code(db) -> str:
    """Generate a unique referral code by checking database existence."""
    while True:
        code = _generate_referral_code()
        existing = await db.users.find_one({"referral_code": code})
        if not existing:
            return code


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(payload: UserRegister):
    """Register a new user account.

    Validates phone uniqueness, hashes the password, generates a unique
    referral code, and returns a signed JWT token with the user profile.
    """
    db = get_db()

    existing_user = await db.users.find_one({"phone": payload.phone})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": "Phone number is already registered",
                "code": "USER_EXISTS",
            },
        )

    password_hash = hash_password(payload.password)
    user_uid = str(uuid.uuid4())
    referral_code = await _ensure_unique_referral_code(db)
    now = datetime.now(timezone.utc)

    user_doc = {
        "uid": user_uid,
        "phone": payload.phone,
        "password_hash": password_hash,
        "name": payload.name,
        "email": None,
        "plan": "free",
        "analyses_used": 0,
        "analyses_limit": 5,
        "fraud_iq_level": "novice",
        "guardian_points": 0,
        "badges": [],
        "referral_code": referral_code,
        "referred_by": None,
        "created_at": now,
        "updated_at": now,
    }

    await db.users.insert_one(user_doc)
    logger.info("New user registered: %s (%s)", user_uid, payload.phone)

    token_data = {"uid": user_uid, "phone": payload.phone, "plan": "free"}
    access_token = create_access_token(token_data)

    profile = UserProfile(**user_doc)

    return {
        "success": True,
        "data": TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=profile,
        ).model_dump(),
        "message": "User registered successfully",
    }


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="User login",
)
async def login(payload: UserLogin):
    """Authenticate a user by phone number and password.

    Returns a signed JWT access token with the user profile on success.
    """
    db = get_db()

    user_doc = await db.users.find_one({"phone": payload.phone})
    if not user_doc or not verify_password(
        payload.password, user_doc.get("password_hash", "")
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": "Invalid phone number or password",
                "code": "INVALID_CREDENTIALS",
            },
        )

    token_data = {
        "uid": user_doc["uid"],
        "phone": user_doc["phone"],
        "plan": user_doc["plan"],
    }
    access_token = create_access_token(token_data)
    profile = UserProfile(**user_doc)

    logger.info("User logged in: %s", user_doc["uid"])

    return {
        "success": True,
        "data": TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=profile,
        ).model_dump(),
        "message": "Login successful",
    }


@router.get(
    "/profile",
    status_code=status.HTTP_200_OK,
    summary="Get user profile",
)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Retrieve the authenticated user's profile information."""
    db = get_db()

    user_doc = await db.users.find_one({"uid": current_user["uid"]})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": "User profile not found",
                "code": "USER_NOT_FOUND",
            },
        )

    profile = UserProfile(**user_doc)

    return {
        "success": True,
        "data": profile.model_dump(),
        "message": "Profile retrieved successfully",
    }


@router.put(
    "/profile",
    status_code=status.HTTP_200_OK,
    summary="Update user profile",
)
async def update_profile(
    payload: UserUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update name, email, or fraud IQ level in the user's profile."""
    db = get_db()
    now = datetime.now(timezone.utc)

    update_fields: dict = {}
    if payload.name is not None:
        update_fields["name"] = payload.name
    if payload.email is not None:
        update_fields["email"] = payload.email
    if payload.fraud_iq_level is not None:
        update_fields["fraud_iq_level"] = payload.fraud_iq_level

    if update_fields:
        update_fields["updated_at"] = now
        await db.users.update_one(
            {"uid": current_user["uid"]},
            {"$set": update_fields},
        )

    user_doc = await db.users.find_one({"uid": current_user["uid"]})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "success": False,
                "error": "User profile not found",
                "code": "USER_NOT_FOUND",
            },
        )

    profile = UserProfile(**user_doc)

    return {
        "success": True,
        "data": profile.model_dump(),
        "message": "Profile updated successfully",
    }


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
)
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """Issue a new access token for the authenticated user."""
    token_data = {
        "uid": current_user["uid"],
        "phone": current_user["phone"],
        "plan": current_user["plan"],
    }
    new_token = create_access_token(token_data)

    return {
        "success": True,
        "data": {"access_token": new_token, "token_type": "bearer"},
        "message": "Token refreshed successfully",
    }
