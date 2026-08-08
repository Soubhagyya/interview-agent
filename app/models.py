from typing import Any, Optional
from pydantic import BaseModel


class InterviewRequest(BaseModel):
    sessionId: str
    candidate: Optional[dict[str, Any]] = None
    message: Optional[str] = None


class Feedback(BaseModel):
    summary: str
    strengths: list[str]
    gaps: list[str]
    next: list[str]


class InterviewResponse(BaseModel):
    reply: str
    done: bool
    feedback: Optional[Feedback] = None
