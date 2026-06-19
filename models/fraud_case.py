"""Fraud analysis and database lookup Pydantic schemas.

Contains models for screenshot analyses, entity lookup requests,
and search query responses.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class AnalysisResponse(BaseModel):
    """Schema representing the result of a screenshot fraud analysis."""

    analysis_id: str = Field(..., description="UUID4 string identifying the analysis")
    verdict: str = Field(..., description="Verdict (safe/medium_risk/high_risk/unknown)")
    confidence_score: int = Field(..., ge=0, le=100, description="Confidence score (0-100)")
    scam_type: str = Field(..., description="Detected scam category or type")
    explanation_en: str = Field(..., description="Detailed explanation in English")
    explanation_hi: str = Field(..., description="Detailed explanation in Hindi")
    recommended_action: str = Field(..., description="Recommended actions for the user")
    image_url: str = Field(..., description="Secure Cloudinary image URL")
    created_at: datetime = Field(..., description="UTC creation timestamp")


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
    """Response schema for UPI, Phone, and URL lookups."""

    is_reported: bool = Field(..., description="Indicates if the entity has been reported")
    report_count: int = Field(0, description="Total reports for this entity")
    scam_categories: List[str] = Field(default_factory=list, description="Associated scam categories")
    risk_level: str = Field("safe", description="Calculated risk level (safe/medium_risk/high_risk)")
    reason: Optional[str] = Field(None, description="Optional explanation or reason for URL status")
