from __future__ import annotations

import json

from anthropic import AsyncAnthropic

from app.config import Settings
from app.services.llm_client import LlmClient, LlmDigestResult, LlmGrantScore, LlmInvestorScore, LlmSignalAnalysis


class AnthropicLlmClient(LlmClient):
    def __init__(self, *, settings: Settings) -> None:
        self._client = AsyncAnthropic(api_key=settings.anthropic_api_key, timeout=settings.request_timeout_seconds)
        self._model = settings.llm_model
        self._max_tokens = settings.llm_max_tokens

    async def _json_call(self, *, system: str, user: str) -> dict:
        message = await self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )

        text = ""
        for block in message.content:
            if getattr(block, "type", None) == "text":
                text += block.text

        return json.loads(text)

    async def score_investor(
        self,
        *,
        client_name: str,
        client_thesis: str,
        investor_name: str,
        investor_notes: str | None,
    ) -> LlmInvestorScore:
        notes_section = (
            f"\nPerplexity-enriched thesis context (use this to improve thesis_alignment scoring):\n{investor_notes}"
            if investor_notes
            else ""
        )
        payload = await self._json_call(
            system="You are a strict JSON-only scoring engine. Output ONLY valid JSON.",
            user=(
                "Score an investor against a client thesis.\n"
                f"Client: {client_name}\n"
                f"Thesis: {client_thesis}\n"
                f"Investor: {investor_name}"
                f"{notes_section}\n\n"
                "Return JSON with keys: thesis_alignment, stage_fit, check_size_fit, strategic_value (0-100 ints), "
                "confidence_score (0.0-1.0), evidence_urls (list of urls), notes (string or null)."
            ),
        )

        return LlmInvestorScore(
            thesis_alignment=int(payload["thesis_alignment"]),
            stage_fit=int(payload["stage_fit"]),
            check_size_fit=int(payload["check_size_fit"]),
            strategic_value=int(payload["strategic_value"]),
            confidence_score=float(payload["confidence_score"]),
            evidence_urls=list(payload.get("evidence_urls") or []),
            notes=payload.get("notes"),
        )

    async def analyze_signal(self, *, signal_type: str, title: str, url: str, raw_text: str | None) -> LlmSignalAnalysis:
        payload = await self._json_call(
            system="You are a strict JSON-only analyst. Output ONLY valid JSON.",
            user=(
                "Analyze an inbound signal for priority routing.\n"
                f"Signal type: {signal_type}\n"
                f"Title: {title}\n"
                f"URL: {url}\n"
                f"Raw text (optional): {raw_text or ''}\n\n"
                "Return JSON with keys: priority (HIGH|MEDIUM|LOW), confidence_score (0.0-1.0), "
                "rationale (string), categories (list of strings), evidence_urls (list of urls)."
            ),
        )

        return LlmSignalAnalysis(
            priority=str(payload["priority"]),
            confidence_score=float(payload["confidence_score"]),
            rationale=str(payload["rationale"]),
            categories=list(payload.get("categories") or []),
            evidence_urls=list(payload.get("evidence_urls") or []),
        )

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
        market_section = (
            f"\nReal-time market context (use for the Market Pulse section):\n{market_context}"
            if market_context
            else ""
        )
        investor_section = ""
        if investors:
            investor_lines = "\n".join(
                f"  - {name} (pipeline: {status or 'unknown'})" for name, status in investors
            )
            investor_section = (
                f"\nInvestor pipeline status (tailor outreach commentary accordingly):\n{investor_lines}"
            )

        payload = await self._json_call(
            system="You are a strict JSON-only digest generator. Output ONLY valid JSON.",
            user=(
                "Generate a weekly digest for a client.\n"
                f"Client: {client_name}\n"
                f"Week: {week_start} to {week_end}"
                f"{market_section}"
                f"{investor_section}\n"
                f"Signals: {signals}\n\n"
                "Return JSON with keys: subject (string), preheader (string), sections (list of objects with title and bullets)."
            ),
        )

        sections = []
        for section in payload["sections"]:
            sections.append((str(section["title"]), [str(b) for b in (section.get("bullets") or [])]))

        return LlmDigestResult(
            subject=str(payload["subject"]),
            preheader=str(payload["preheader"]),
            sections=sections,
        )

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
        payload = await self._json_call(
            system="You are a strict JSON-only grant scoring engine for life sciences companies. Output ONLY valid JSON.",
            user=(
                "Score a federal grant opportunity against a client profile.\n\n"
                "CLIENT PROFILE:\n"
                f"  Company: {company_name}\n"
                f"  Therapeutic area: {therapeutic_area}\n"
                f"  Stage: {stage}\n"
                f"  FDA pathway: {fda_pathway or 'not specified'}\n"
                f"  Keywords: {', '.join(keywords)}\n\n"
                "GRANT OPPORTUNITY:\n"
                f"  Title: {grant_title}\n"
                f"  Agency: {grant_agency}\n"
                f"  Program: {grant_program or 'not specified'}\n"
                f"  Award amount: {grant_award_amount or 'not specified'}\n"
                f"  Deadline: {grant_deadline or 'not specified'}\n"
                f"  Description: {grant_description or 'not provided'}\n"
                f"  Eligibility: {grant_eligibility or 'not provided'}\n\n"
                "Scoring weights: therapeutic_match 35%, stage_eligibility 25%, "
                "award_size_relevance 15%, deadline_feasibility 15%, historical_funding 10%.\n\n"
                "If grant description is vague or eligibility criteria are unclear, set confidence to 'low'. "
                "Do not fabricate eligibility assessments.\n\n"
                "Return JSON with keys: overall_score (0-100 int), "
                "therapeutic_match (0-100 int), stage_eligibility (0-100 int), "
                "award_size_relevance (0-100 int), deadline_feasibility (0-100 int), "
                "historical_funding (0-100 int), rationale (string), "
                "application_guidance (string or null), confidence ('high'|'medium'|'low')."
            ),
        )

        return LlmGrantScore(
            overall_score=int(payload["overall_score"]),
            therapeutic_match=int(payload["therapeutic_match"]),
            stage_eligibility=int(payload["stage_eligibility"]),
            award_size_relevance=int(payload["award_size_relevance"]),
            deadline_feasibility=int(payload["deadline_feasibility"]),
            historical_funding=int(payload["historical_funding"]),
            rationale=str(payload["rationale"]),
            application_guidance=payload.get("application_guidance"),
            confidence=str(payload["confidence"]),
        )
