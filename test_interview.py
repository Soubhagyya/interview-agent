import json
import requests

BASE_URL = BASE_URL = "https://interview-agent-lpzr.onrender.com/api/interview"
SESSION_ID = "test-session-1"

with open("data/candidates.json") as f:
    candidates = json.load(f)["candidates"]

candidate = candidates[0]
print(f"Testing interview for: {candidate['member']['name']}\n")

resp = requests.post(BASE_URL, json={"sessionId": SESSION_ID, "candidate": candidate})
data = resp.json()
print("INTERVIEWER:", data["reply"])

while not data.get("done"):
    answer = input("\nYOUR ANSWER: ")
    resp = requests.post(BASE_URL, json={"sessionId": SESSION_ID, "message": answer})
    data = resp.json()
    print("\nINTERVIEWER:", data["reply"])

if data.get("feedback"):
    print("\n\n=== FINAL FEEDBACK ===")
    print(json.dumps(data["feedback"], indent=2))