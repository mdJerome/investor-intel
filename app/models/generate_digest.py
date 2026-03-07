from __future__ import annotations

from pydantic import BaseModel, Field

from app.config import DEFAULT_SCHEMA_VERSION
from app.models.score_investors import PipelineStatus


class DigestClient(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    geography: str | None = Field(default=None, max_length=200)


class DigestSignal(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    url: str = Field(min_length=1, max_length=2000)
    summary: str | None = Field(default=None, max_length=4000)


class DigestInvestor(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    pipeline_status: PipelineStatus | None = Field(default=None)


class GenerateDigestRequest(BaseModel):
    schema_version: str = Field(default=DEFAULT_SCHEMA_VERSION, max_length=32)
    client: DigestClient
    week_start: str = Field(min_length=1, max_length=32)
    week_end: str = Field(min_length=1, max_length=32)
    signals: list[DigestSignal] = Field(default_factory=list, max_length=200)
    investors: list[DigestInvestor] = Field(default_factory=list, max_length=200)
    market_context: str | None = Field(default=None, max_length=8000)


class DigestSection(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    bullets: list[str] = Field(default_factory=list, max_length=50)


class DigestPayload(BaseModel):
    subject: str = Field(min_length=1, max_length=200)
    preheader: str = Field(min_length=1, max_length=300)
    sections: list[DigestSection] = Field(min_length=1, max_length=20)


class GenerateDigestResponse(BaseModel):
    schema_version: str = Field(default=DEFAULT_SCHEMA_VERSION, max_length=32)
    payload: DigestPayload
