\# AI Interview Agent



An autonomous, adaptive AI technical interviewer built for the ABTalks Vibe Code Hackathon

(Problem Statement 2). It conducts a multi-turn conversational interview based on a candidate's

actual learning history, asks genuine follow-up questions grounded in their answers, and

produces structured feedback at the end.



\*\*Live demo (chat UI):\*\* https://interview-agent-lpzr.onrender.com/demo

\*\*API endpoint:\*\* https://interview-agent-lpzr.onrender.com/api/interview



\## How it works



\- `app/curriculum.py` — builds a topic plan per candidate, prioritizing skipped missions,

&#x20; then struggled (high-attempt) missions, then quickly-passed missions — each with a stated

&#x20; editorial rationale.

\- `app/interview\_engine.py` — a session state machine tracking topic/question progression,

&#x20; guaranteeing 8+ questions across 4+ curriculum days per the spec.

\- `app/llm.py` — generates the opening question, adaptive follow-ups, topic transitions, and

&#x20; final structured feedback using Google Gemini's free tier (OpenAI-compatible endpoint). Falls

&#x20; back to template-based questions/feedback if the LLM call fails, so the API never breaks.

\- `app/static/chat.html` — a simple browser chat UI on top of the same API, for live demoing.



\## Run locally



1\. `pip install -r requirements.txt`

2\. Copy `.env.example` to `.env` and paste your \*\*free Gemini API key\*\*

&#x20;  (get one at https://aistudio.google.com/apikey — no credit card needed)

3\. `uvicorn app.main:app --reload --port 8000`

4\. POST to `http://localhost:8000/api/interview`, or open `http://localhost:8000/demo` for the chat UI



See `PROMPTS.md` for the AI usage log.

