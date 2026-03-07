from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LlmInvestorScore:
    thesis_alignment: int
    stage_fit: int
    check_size_fit: int
    strategic_value: int
    notes: str | None
    evidence_urls: list[str]
    confidence_score: float


@dataclass(frozen=True)
class LlmSignalAnalysis:
    priority: str
    rationale: str
    categories: list[str]
    evidence_urls: list[str]
    confidence_score: float


@dataclass(frozen=True)
class LlmDigestResult:
    subject: str
    preheader: str
    sections: list[tuple[str, list[str]]]


@dataclass(frozen=True)
class LlmGrantScore:
    overall_score: int
    therapeutic_match: int
    stage_eligibility: int
    award_size_relevance: int
    deadline_feasibility: int
    historical_funding: int
    rationale: str
    application_guidance: str | None
    confidence: str  # "high" | "medium" | "low"


class LlmClient(Protocol):
    async def score_investor(
        self,
        *,
        client_name: str,
        client_thesis: str,
        investor_name: str,
        investor_notes: str | None,
    ) -> LlmInvestorScore:
        raise NotImplementedError

    async def analyze_signal(self, *, signal_type: str, title: str, url: str, raw_text: str | None) -> LlmSignalAnalysis:
        raise NotImplementedError

    async def generate_digest(
        self,
        *,
        client_name: str,
        week_start: str,
        week_end: str,
        signals: list[tuple[str, str]],
        investors: list[tuple[str, str | None]],
        market_context: str | None,
    ) -> LlmDigestResult:
        raise NotImplementedError

    async def score_grant(
        self,
        *,
        company_name: str,
        therapeutic_area: str,
        stage: str,
        fda_pathway: str | None,
        keywords: list[str],
        grant_title: str,
        grant_agency: str,
        grant_program: str | None,
        grant_description: str | None,
        grant_eligibility: str | None,
        grant_award_amount: str | None,
        grant_deadline: str | None,
    ) -> LlmGrantScore:
        raise NotImplementedError
