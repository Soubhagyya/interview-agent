# AI Interview Agent

Run locally:
1. pip install -r requirements.txt
2. Copy .env.example to .env and paste your OpenAI key
3. uvicorn app.main:app --reload --port 8000
4. POST to http://localhost:8000/api/interview

See PROMPTS.md for AI usage log.
