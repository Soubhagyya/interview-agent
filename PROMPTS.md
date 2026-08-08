\# AI Usage Log



This project was built with Claude (Anthropic) as an AI pair-programmer during the hackathon.



\## What Claude helped build

\- FastAPI backend exposing the required `/api/interview` endpoint per the technical spec

\- Topic-selection engine (`app/curriculum.py`) that prioritizes interview topics based on

&#x20; candidate signals: skipped missions, high-attempt (struggled) missions, and quickly-passed

&#x20; missions — each with a stated rationale

\- Multi-turn interview state machine (`app/interview\_engine.py`) tracking session state,

&#x20; question count, topic/day coverage, and conversation transcript

\- LLM integration (`app/llm.py`) using Google Gemini's free tier via an OpenAI-compatible

&#x20; endpoint, generating adaptive follow-up questions grounded in the candidate's actual answers

\- Structured feedback generation (summary/strengths/gaps/next) from the full transcript

\- A local fallback (template-based questions/feedback) if the LLM call fails, so the API

&#x20; never breaks even under free-tier rate limits

\- Deployment configuration (Procfile, requirements.txt) for Render



\## Key prompts used

\- "Build an AI Interview Agent per this technical spec: \[pasted spec]. Use the candidate

&#x20; and curriculum JSON provided. Python/FastAPI backend, Gemini free tier for the LLM."

\- "Design topic selection so skipped/struggled missions get prioritized with an editorial

&#x20; rationale, ensuring at least 4 distinct curriculum days and 8+ questions."

\- "Add a safe fallback so the interview still works if the LLM call fails."

\- Iterative debugging prompts while setting up the local environment, `.env` key handling,

&#x20; and Render deployment (dependency fixes, path issues).



\## What I (the developer) did

\- Set up local Python environment, ran and tested the app

\- Created and managed API keys and environment variables

\- Created the GitHub repository and pushed the code

\- Deployed and configured the live service on Render

\- Verified the live endpoint against the spec before submission

