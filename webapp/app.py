#!/usr/bin/env python3
"""
FastAPI web app wrapper for the resume builder.
"""

from __future__ import annotations

from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Import your resume builder logic
from tools.resume_builder import ResumeBuilder


# ✅ Initialize FastAPI app
app = FastAPI(
    title="Resume Builder API",
    version="1.0.0"
)


# -----------------------------
# 📦 Request / Response Models
# -----------------------------

class ResumeRequest(BaseModel):
    data: Dict[str, Any] = Field(
        ...,
        description="Structured resume input payload"
    )


class ResumeResponse(BaseModel):
    resume_markdown: str
    missing_required_context: List[str]


# -----------------------------
# 🩺 Health Check
# -----------------------------

@app.get("/")
def root():
    return {"message": "Resume Builder API is running 🚀"}


@app.get("/health")
def health():
    return {"status": "ok"}


# -----------------------------
# 🧠 Resume Generation Endpoint
# -----------------------------

@app.post("/build-resume", response_model=ResumeResponse)
def build_resume(payload: ResumeRequest) -> ResumeResponse:
    try:
        # Initialize builder with input data
        builder = ResumeBuilder(data=payload.data)

        # Generate resume
        resume_markdown = builder.render()

        # Check missing fields
        missing_required_context = builder.missing_required_context()

        return ResumeResponse(
            resume_markdown=resume_markdown,
            missing_required_context=missing_required_context
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating resume: {str(e)}"
        )
