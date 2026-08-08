import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

with open(DATA_DIR / "curriculum.json") as f:
    CURRICULUM = json.load(f)

DAYS_BY_NUMBER = {d["day"]: d for d in CURRICULUM["days"]}


def get_day(day_number: int) -> dict:
    return DAYS_BY_NUMBER.get(day_number)


def build_topic_plan(candidate: dict, max_topics: int = 5) -> list[dict]:
    """
    Decide which curriculum days to interview this candidate on, and why.
    Priority order:
      1. Missions they SKIPPED       -> test if they can reason about it anyway
      2. Missions passed with many attempts (>=3) -> they struggled, probe depth
      3. Missions passed on first/second try -> confirm real understanding
    Ensures topic diversity across different curriculum days.
    """
    missions = candidate.get("missions", [])

    skipped = [m for m in missions if m.get("skipped")]
    struggled = [m for m in missions if m.get("passed") and m.get("attempts", 1) >= 3]
    strong = [m for m in missions if m.get("passed") and m.get("attempts", 1) <= 2]

    # Order candidates for interviewing: skipped first (biggest editorial signal),
    # then struggled (probe understanding vs memorization), then strong (verify depth)
    ordered = skipped + struggled + strong

    plan = []
    seen_days = set()
    for m in ordered:
        day_num = m["day"]
        if day_num in seen_days:
            continue
        day_info = get_day(day_num)
        if not day_info:
            continue
        seen_days.add(day_num)

        if m.get("skipped"):
            reason = f"Candidate skipped Day {day_num} ({day_info['title']}) entirely — probing whether they understand the concept despite skipping the mission."
        elif m.get("attempts", 1) >= 3:
            reason = f"Candidate needed {m['attempts']} attempts to pass Day {day_num} ({day_info['title']}) — checking if understanding is solid or memorized."
        else:
            reason = f"Candidate passed Day {day_num} ({day_info['title']}) quickly — verifying depth of understanding, not just surface recall."

        plan.append({
            "day": day_num,
            "title": day_info["title"],
            "objectives": day_info.get("objectives", []),
            "tools": day_info.get("tools", []),
            "reason": reason,
        })

        if len(plan) >= max_topics:
            break

    return plan
