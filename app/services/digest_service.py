from __future__ import annotations

from app.models.generate_digest import (
    DigestPayload,
    DigestSection,
    GenerateDigestRequest,
    GenerateDigestResponse,
)
from app.services.llm_client import LlmClient


class DigestService:
    def __init__(self, *, llm: LlmClient) -> None:
        self._llm = llm

    async def generate(self, req: GenerateDigestRequest) -> GenerateDigestResponse:
        llm_result = await self._llm.generate_digest(
            client_name=req.client.name,
            week_start=req.week_start,
            week_end=req.week_end,
            signals=[(s.title, s.url) for s in req.signals],
            investors=[(inv.name, inv.pipeline_status) for inv in req.investors],
            market_context=req.market_context,
        )

        sections = [DigestSection(title=title, bullets=bullets) for (title, bullets) in llm_result.sections]
        payload = DigestPayload(subject=llm_result.subject, preheader=llm_result.preheader, sections=sections)
        return GenerateDigestResponse(payload=payload)
