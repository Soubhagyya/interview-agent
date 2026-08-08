from app.curriculum import build_topic_plan
from app import llm

# In-memory session store. sessionId -> state dict.
# Fine for a hackathon submission (single process). Swap for Redis/DB for real prod use.
SESSIONS: dict[str, dict] = {}

QUESTIONS_PER_TOPIC = 2  # main + 1 follow-up = guarantees 2 * topics questions
MIN_TOPICS = 4


def start_session(session_id: str, candidate: dict) -> dict:
    member = candidate.get("member", {})
    name = member.get("name", "Candidate")
    role = member.get("jobRole", "AI practitioner")

    topics = build_topic_plan(candidate, max_topics=5)
    if len(topics) < MIN_TOPICS:
        # pad safety net in case candidate has very few missions
        topics = topics * ((MIN_TOPICS // max(len(topics), 1)) + 1)
        topics = topics[:MIN_TOPICS]

    state = {
        "candidate_name": name,
        "job_role": role,
        "topics": topics,
        "topic_index": 0,
        "sub_step": 0,  # 0 = need main question, 1 = need follow-up
        "question_count": 0,
        "transcript": [],  # [{"role": "interviewer"/"candidate", "content": str, "day": int}]
        "current_question": None,
        "done": False,
    }
    SESSIONS[session_id] = state

    first_topic = topics[0]
    opening = llm.generate_opening_question(name, role, first_topic)

    state["transcript"].append({"role": "interviewer", "content": opening, "day": first_topic["day"]})
    state["current_question"] = opening
    state["question_count"] = 1
    state["sub_step"] = 1  # next candidate answer should trigger a follow-up

    return {"reply": opening, "done": False}


def continue_session(session_id: str, message: str) -> dict:
    state = SESSIONS.get(session_id)
    if state is None:
        return {"reply": "Session not found. Please start a new interview.", "done": True,
                "feedback": {"summary": "Invalid session.", "strengths": [], "gaps": [], "next": []}}

    if state["done"]:
        return {"reply": "This interview has already concluded.", "done": True}

    state["transcript"].append({"role": "candidate", "content": message,
                                 "day": state["topics"][state["topic_index"]]["day"]})

    topic = state["topics"][state["topic_index"]]

    days_covered = len({t["day"] for t in state["topics"][:state["topic_index"] + 1]})
    ready_to_wrap = (state["question_count"] >= 8 and days_covered >= MIN_TOPICS
                      and state["sub_step"] == 1
                      and state["topic_index"] >= len(state["topics"]) - 1)

    if ready_to_wrap:
        return _finish_interview(state)

    if state["sub_step"] == 1:
        # give a follow-up on the same topic
        followup = llm.generate_followup(
            state["candidate_name"], topic, state["current_question"], message
        )
        state["transcript"].append({"role": "interviewer", "content": followup, "day": topic["day"]})
        state["current_question"] = followup
        state["question_count"] += 1
        state["sub_step"] = 2
        return {"reply": followup, "done": False}

    else:
        # move to next topic, or wrap up if none left
        if state["topic_index"] + 1 >= len(state["topics"]):
            return _finish_interview(state)

        state["topic_index"] += 1
        next_topic = state["topics"][state["topic_index"]]
        bridge = llm.generate_transition_question(state["candidate_name"], topic, next_topic)
        state["transcript"].append({"role": "interviewer", "content": bridge, "day": next_topic["day"]})
        state["current_question"] = bridge
        state["question_count"] += 1
        state["sub_step"] = 1
        return {"reply": bridge, "done": False}


def _finish_interview(state: dict) -> dict:
    state["done"] = True
    feedback = llm.generate_feedback(state["candidate_name"], state["job_role"], state["transcript"])
    return {
        "reply": "That concludes our interview today. Thank you for your time — here is your feedback.",
        "done": True,
        "feedback": feedback,
    }
