"""
FraudShield AI — Community Alert Pydantic Schemas
===================================================
Models for community-submitted fraud alerts that are displayed on the
Community page, including vote tracking and verification status.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class CommunityAlertCreate(BaseModel):
    """Schema for creating a new community fraud alert."""

    author: str = Field(..., min_length=1, description="Author name")
    author_avatar: Optional[str] = Field(None, description="Author avatar URL")
    title: str = Field(..., min_length=5, description="Alert headline")
    category: Literal[
        "UPI Scam",
        "Fake Job",
        "Bank Impersonation",
        "Crypto Fraud",
        "Phishing Link",
        "Other",
    ] = Field(..., description="Alert category")
    description: str = Field(..., min_length=10, description="Alert description")
    risk_level: str = Field("HIGH", description="Risk level (SAFE/MEDIUM/HIGH/CRITICAL)")
    location: str = Field(..., min_length=1, description="Geographic location")
    tags: List[str] = Field(default_factory=list, description="Descriptive tags")


class CommunityAlertResponse(BaseModel):
    """Schema representing a community alert returned in API responses."""

    id: str = Field(..., description="Unique alert identifier")
    author: str = Field(..., description="Author name")
    author_avatar: Optional[str] = Field(None, alias="authorAvatar")
    title: str = Field(..., description="Alert headline")
    category: str = Field(..., description="Alert category")
    description: str = Field(..., description="Alert description")
    risk_level: str = Field(..., alias="riskLevel", description="Risk level")
    location: str = Field(..., description="Geographic location")
    votes: int = Field(0, description="Community vote count")
    verified: bool = Field(False, description="Verification status")
    timestamp: str = Field(..., description="Human-readable timestamp")
    tags: List[str] = Field(default_factory=list, description="Descriptive tags")
    created_at: Optional[datetime] = Field(None, description="UTC creation timestamp")

    model_config = {"populate_by_name": True}


class VotePayload(BaseModel):
    """Schema for voting on a community alert."""

    delta: int = Field(..., description="Vote delta (+1 or -1)")
