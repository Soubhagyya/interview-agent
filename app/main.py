from dotenv import load_dotenv
load_dotenv()

import json
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
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

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
STATIC_DIR = Path(__file__).resolve().parent / "static"


@app.get("/")
def health():
    return {"status": "ok", "service": "ai-interview-agent"}


@app.get("/demo", response_class=HTMLResponse)
def demo_page():
    return (STATIC_DIR / "chat.html").read_text()


@app.get("/api/demo-candidate")
def demo_candidate():
    with open(DATA_DIR / "candidates.json") as f:
        candidates = json.load(f)["candidates"]
    return candidates[0]


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
        return InterviewResponse(reply=f"ERROR: {type(e).__name__}: {str(e)}", done=True)