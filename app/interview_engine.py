from app.curriculum import build_topic_plan
from app import llm

SESSIONS: dict[str, dict] = {}

MIN_TOPICS = 4


def _progress(state: dict) -> dict:
    return {
        "topicsCovered": state["topic_index"] + 1,
        "totalTopics": len(state["topics"]),
        "questionsAsked": state["question_count"],
    }


def start_session(session_id: str, candidate: dict) -> dict:
    member = candidate.get("member", {})
    name = member.get("name", "Candidate")
    role = member.get("jobRole", "AI practitioner")

    topics = build_topic_plan(candidate, max_topics=5)
    if len(topics) < MIN_TOPICS:
        topics = topics * ((MIN_TOPICS // max(len(topics), 1)) + 1)
        topics = topics[:MIN_TOPICS]

    state = {
        "candidate_name": name,
        "job_role": role,
        "topics": topics,
        "topic_index": 0,
        "sub_step": 0,
        "question_count": 0,
        "transcript": [],
        "current_question": None,
        "done": False,
    }
    SESSIONS[session_id] = state

    first_topic = topics[0]
    opening = llm.generate_opening_question(name, role, first_topic)

    state["transcript"].append({"role": "interviewer", "content": opening, "day": first_topic["day"]})
    state["current_question"] = opening
    state["question_count"] = 1
    state["sub_step"] = 1

    return {
        "reply": opening,
        "done": False,
        "currentTopic": first_topic["title"],
        "topicRationale": first_topic["reason"],
        "progress": _progress(state),
    }


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
        followup = llm.generate_followup(
            state["candidate_name"], topic, state["current_question"], message
        )
        state["transcript"].append({"role": "interviewer", "content": followup, "day": topic["day"]})
        state["current_question"] = followup
        state["question_count"] += 1
        state["sub_step"] = 2
        return {
            "reply": followup,
            "done": False,
            "currentTopic": topic["title"],
            "topicRationale": topic["reason"],
            "progress": _progress(state),
        }

    else:
        if state["topic_index"] + 1 >= len(state["topics"]):
            return _finish_interview(state)

        state["topic_index"] += 1
        next_topic = state["topics"][state["topic_index"]]
        bridge = llm.generate_transition_question(state["candidate_name"], topic, next_topic)
        state["transcript"].append({"role": "interviewer", "content": bridge, "day": next_topic["day"]})
        state["current_question"] = bridge
        state["question_count"] += 1
        state["sub_step"] = 1
        return {
            "reply": bridge,
            "done": False,
            "currentTopic": next_topic["title"],
            "topicRationale": next_topic["reason"],
            "progress": _progress(state),
        }


def _finish_interview(state: dict) -> dict:
    state["done"] = True
    feedback = llm.generate_feedback(state["candidate_name"], state["job_role"], state["transcript"])
    return {
        "reply": "That concludes our interview today. Thank you for your time — here is your feedback.",
        "done": True,
        "feedback": feedback,
        "progress": _progress(state),
    }