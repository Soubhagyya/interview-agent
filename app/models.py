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


class ScorecardEntry(BaseModel):
    topic: str
    score: float


class Progress(BaseModel):
    topicsCovered: int
    totalTopics: int
    questionsAsked: int
    scorecard: list[ScorecardEntry] = []


class InterviewResponse(BaseModel):
    reply: str
    done: bool
    feedback: Optional[Feedback] = None
    currentTopic: Optional[str] = None
    topicRationale: Optional[str] = None
    progress: Optional[Progress] = None