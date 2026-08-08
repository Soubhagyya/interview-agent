from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models import InterviewRequest, InterviewResponse
from app import interview_engine

app = FastAPI(title="AI Interview Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return {"status": "ok", "service": "ai-interview-agent"}


@app.post("/api/interview", response_model=InterviewResponse)
def interview(req: InterviewRequest):
    session_id = req.sessionId
    try:
        if session_id not in interview_engine.SESSIONS:
            if req.candidate is None:
                return InterviewResponse(
                    reply="A candidate profile is required to start a new session.",
                    done=True,
                )
            result = interview_engine.start_session(session_id, req.candidate)
            return InterviewResponse(**result)

        result = interview_engine.continue_session(session_id, req.message or "")
        return InterviewResponse(**result)
    except Exception as e:
        key = os.environ.get("GEMINI_API_KEY", "")
        debug = f"key_length={len(key)} key_start={key[:6]!r} key_end={key[-4:]!r}"
        return InterviewResponse(reply=f"ERROR: {type(e).__name__}: {str(e)} | {debug}", done=True)