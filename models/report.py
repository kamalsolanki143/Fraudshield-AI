"""Fraud report submission and response Pydantic schemas.

Contains models for creating a report, listing reports, and submission replies.
"""

from datetime import datetime
from typing import List, Literal
from pydantic import BaseModel, Field


class ReportCreate(BaseModel):
    """Schema for submitting a new fraud report."""

    entity_type: Literal["upi_id", "phone_number", "website", "message"] = Field(
        ..., description="Type of entity being reported"
    )
    entity_value: str = Field(..., min_length=1, description="Value of the entity (e.g., UPI ID, phone, URL, message content)")
    scam_category: str = Field(..., min_length=1, description="Scam category (e.g., refund_scam, fake_qr)")
    description: str = Field(..., min_length=5, description="Detailed description of the scam incident")


class ReportResponse(BaseModel):
    """Schema representing a retrieved fraud report."""

    report_id: str = Field(..., description="UUID4 string identifying the report")
    reporter_uid: str = Field(..., description="UID of the reporting user")
    entity_type: str = Field(..., description="Type of entity reported")
    entity_value: str = Field(..., description="Value of the entity reported")
    scam_category: str = Field(..., description="Scam category")
    description: str = Field(..., description="Detailed description")
    verified: bool = Field(False, description="Verification status by moderators")
    upvotes: int = Field(0, description="Number of community upvotes")
    created_at: datetime = Field(..., description="UTC creation timestamp")


class ReportSubmitResponse(BaseModel):
    """Response returned upon successfully submitting a report, detailing points and badges awarded."""

    report_id: str = Field(..., description="UUID4 string of the created report")
    points_awarded: int = Field(..., description="Guardian points awarded (e.g., 10)")
    badges_earned: List[str] = Field(default_factory=list, description="List of newly earned badges")
