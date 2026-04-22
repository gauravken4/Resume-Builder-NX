#!/usr/bin/env python3
"""FastAPI web app wrapper for the resume builder."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from tools.resume_builder import ResumeBuilder

app = FastAPI(title="Resume Builder API", version="1.0.0")


class ResumeRequest(BaseModel):
    data: dict[str, Any] = Field(..., description="Structured resume input payload")


class ResumeResponse(BaseModel):
    resume_markdown: str
    missing_required_context: list[str]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/build-resume", response_model=ResumeResponse)
def build_resume(payload: ResumeRequest) -> ResumeResponse:
    try:
        builder = ResumeBuilder(data=payload.data)
        resume_markdown = builder.render()
        missing_required_context = builder.missing_required_context()
        return ResumeResponse(
            resume_markdown=resume_markdown,
            missing_required_context=missing_required_context,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Unable to build resume: {exc}") from exc
