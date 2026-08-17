"""
FraudShield AI — Fraud Analysis Pydantic Schemas
==================================================
Models for screenshot analysis responses, entity-lookup requests (UPI, phone,
URL), and lookup response payloads.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class AnalysisResponse(BaseModel):
    """Schema representing the result of a screenshot fraud analysis."""

    analysis_id: str = Field(..., description="UUID4 string identifying the analysis")
    verdict: str = Field(..., description="Verdict (SAFE/SUSPICIOUS/HIGH RISK/CONFIRMED SCAM)")
    risk_score: int = Field(..., ge=0, le=100, description="Risk score (0-100)")
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="AI confidence score (0.0-1.0)"
    )
    scam_type: str = Field(..., description="Detected scam category or type")
    reasons: List[str] = Field(default_factory=list, description="List of fraud indicators")
    action_step: str = Field(..., description="Recommended action for the user")
    risk_level: str = Field(..., description="Color-coded risk level (green/yellow/orange/red)")
    is_dangerous: bool = Field(..., description="Whether score >= 60")
    image_url: str = Field("", description="Secure Cloudinary image URL")
    explanation_en: str = Field("", description="Detailed explanation in English")
    explanation_hi: str = Field("", description="Detailed explanation in Hindi")
    analysed_at: str = Field("", description="ISO-8601 UTC timestamp of analysis")
    created_at: Optional[datetime] = Field(None, description="UTC creation timestamp")


class LookupUPI(BaseModel):
    """Request schema for lookup of a UPI ID."""

    upi_id: str = Field(..., description="UPI address to query (e.g. user@bank)")


class LookupPhone(BaseModel):
    """Request schema for lookup of a phone number."""

    phone_number: str = Field(..., description="Phone number to query")


class LookupURL(BaseModel):
    """Request schema for lookup of a URL."""

    url: str = Field(..., description="URL website link to query")


class LookupResponse(BaseModel):
    """Response schema for UPI, phone, and URL lookups."""

    is_reported: bool = Field(..., description="Indicates if the entity has been reported")
    report_count: int = Field(0, description="Total reports for this entity")
    scam_categories: List[str] = Field(
        default_factory=list, description="Associated scam categories"
    )
    risk_level: str = Field("safe", description="Calculated risk level")
    reason: Optional[str] = Field(None, description="Optional explanation")
