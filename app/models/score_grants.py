from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.config import DEFAULT_SCHEMA_VERSION

GrantConfidence = Literal["high", "medium", "low"]


class GrantClientProfile(BaseModel):
    company_name: str = Field(min_length=1, max_length=200)
    therapeutic_area: str = Field(min_length=1, max_length=500)
    stage: str = Field(min_length=1, max_length=100)
    fda_pathway: str | None = Field(default=None, max_length=200)
    keywords: list[str] = Field(default_factory=list, max_length=20)


class GrantInput(BaseModel):
    source: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=500)
    agency: str = Field(min_length=1, max_length=200)
    program: str | None = Field(default=None, max_length=200)
    award_amount: str | None = Field(default=None, max_length=100)
    deadline: str | None = Field(default=None, max_length=32)
    description: str | None = Field(default=None, max_length=8000)
    eligibility: str | None = Field(default=None, max_length=2000)
    url: str = Field(min_length=1, max_length=2000)


class ScoreGrantsRequest(BaseModel):
    schema_version: str = Field(default=DEFAULT_SCHEMA_VERSION, max_length=32)
    client_profile: GrantClientProfile
    grants: list[GrantInput] = Field(min_length=1, max_length=80)


class GrantScoreBreakdown(BaseModel):
    therapeutic_match: int = Field(ge=0, le=100)
    stage_eligibility: int = Field(ge=0, le=100)
    award_size_relevance: int = Field(ge=0, le=100)
    deadline_feasibility: int = Field(ge=0, le=100)
    historical_funding: int = Field(ge=0, le=100)


class ScoredGrant(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    source: str = Field(min_length=1, max_length=100)
    agency: str = Field(min_length=1, max_length=200)
    program: str | None = Field(default=None, max_length=200)
    award_amount: str | None = Field(default=None, max_length=100)
    deadline: str | None = Field(default=None, max_length=32)
    days_until_deadline: int | None = Field(default=None)
    url: str = Field(min_length=1, max_length=2000)
    overall_score: int = Field(ge=0, le=100)
    breakdown: GrantScoreBreakdown
    rationale: str = Field(min_length=1, max_length=4000)
    application_guidance: str | None = Field(default=None, max_length=4000)
    confidence: GrantConfidence


class ScoreGrantsResponse(BaseModel):
    schema_version: str = Field(default=DEFAULT_SCHEMA_VERSION, max_length=32)
    scored_grants: list[ScoredGrant]
    summary: str = Field(min_length=1, max_length=2000)
