"""
FraudShield AI — User Pydantic Schemas
========================================
Input validation and API serialisation models for user registration, login,
profile retrieval, updates, and authentication token responses.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class UserRegister(BaseModel):
    """Schema for user registration request."""

    phone: str = Field(..., description="Indian phone number")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    name: str = Field(..., min_length=1, description="User's full name")

    @field_validator("phone")
    @classmethod
    def validate_indian_phone(cls, v: str) -> str:
        """Validate Indian phone number format (10 digits, optional country code)."""
        clean_phone = re.sub(r"\s+", "", v)
        pattern = r"^(?:\+91|91)?[6789]\d{9}$"
        if not re.match(pattern, clean_phone):
            raise ValueError("Invalid Indian phone number format")
        return clean_phone


class UserLogin(BaseModel):
    """Schema for user login request."""

    phone: str = Field(..., description="User's phone number")
    password: str = Field(..., description="User's password")


class UserProfile(BaseModel):
    """Schema representing a user profile returned in API responses.

    Excludes sensitive fields like ``password_hash``.
    """

    uid: str = Field(..., description="UUID4 string identifying the user")
    phone: str = Field(..., description="Unique phone number")
    name: str = Field(..., description="Full name")
    email: Optional[str] = Field(None, description="Optional email address")
    plan: str = Field("free", description="Subscription plan (free/pro/family/business)")
    analyses_used: int = Field(0, description="Count of analyses used by the user")
    analyses_limit: int = Field(5, description="Limit of analyses allowed")
    fraud_iq_level: str = Field("novice", description="User's Fraud IQ level")
    guardian_points: int = Field(0, description="Community points earned")
    badges: List[str] = Field(default_factory=list, description="Badges earned by user")
    referral_code: str = Field(..., description="Unique 8-character referral code")
    referred_by: Optional[str] = Field(None, description="UID of referring user")
    created_at: datetime = Field(..., description="Timestamp when created")
    updated_at: datetime = Field(..., description="Timestamp when last updated")


class UserUpdate(BaseModel):
    """Schema for updating user profile fields."""

    name: Optional[str] = Field(None, min_length=1, description="Updated name")
    email: Optional[str] = Field(None, description="Updated email address")
    fraud_iq_level: Optional[str] = Field(
        None, description="Updated Fraud IQ level (novice/aware/vigilant)"
    )

    @field_validator("fraud_iq_level")
    @classmethod
    def validate_iq_level(cls, v: Optional[str]) -> Optional[str]:
        """Ensure the IQ level is one of the valid options."""
        if v is not None and v not in ("novice", "aware", "vigilant"):
            raise ValueError("fraud_iq_level must be 'novice', 'aware', or 'vigilant'")
        return v


class TokenResponse(BaseModel):
    """Schema for a successful authentication response containing JWT token."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type prefix")
    user: UserProfile = Field(..., description="User profile details")
