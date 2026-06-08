"""Authentication API router.

Handles user registration, user login, profile fetching, and profile updates,
conforming to standard response formats.
"""

from datetime import datetime
import random
import string
import uuid
from fastapi import APIRouter, Depends, HTTPException, status

from database.mongodb import get_db
from middleware.auth_middleware import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from models.user import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserProfile,
    UserUpdate,
)

router = APIRouter()


def generate_referral_code() -> str:
    """Generate a random 8-character uppercase alphanumeric referral code."""
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=8))


async def ensure_unique_referral_code(db) -> str:
    """Generate a unique referral code by checking database existence in a loop."""
    while True:
        code = generate_referral_code()
        existing = await db.users.find_one({"referral_code": code})
        if not existing:
            return code


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(payload: UserRegister):
    """Register a new user.

    Validates phone format, checks database constraints, hashes the password,
    generates a unique referral code, and returns a signed JWT token along with
    the user profile.
    """
    db = get_db()

    # Check if user already exists
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

    # Hash the password
    password_hash = hash_password(payload.password)

    # Generate identifiers and keys
    user_uid = str(uuid.uuid4())
    referral_code = await ensure_unique_referral_code(db)
    now = datetime.utcnow()

    # Insert user document with defaults
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

    # Generate JWT Access Token
    token_data = {"uid": user_uid, "phone": payload.phone, "plan": "free"}
    access_token = create_access_token(token_data)

    # Prepare response profile matching UserProfile model
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
    """Authenticate a user by verifying their phone number and password.

    Returns a signed JWT access token along with the user profile on success.
    """
    db = get_db()

    # Find user
    user_doc = await db.users.find_one({"phone": payload.phone})
    if not user_doc or not verify_password(payload.password, user_doc.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": "Invalid phone number or password",
                "code": "INVALID_CREDENTIALS",
            },
        )

    # Generate JWT Access Token
    token_data = {
        "uid": user_doc["uid"],
        "phone": user_doc["phone"],
        "plan": user_doc["plan"],
    }
    access_token = create_access_token(token_data)

    # Prepare response profile matching UserProfile model
    profile = UserProfile(**user_doc)

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
    """Update name, email, or fraud IQ level fields in the user's profile."""
    db = get_db()
    now = datetime.utcnow()

    update_fields = {}
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

    # Retrieve updated document
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
