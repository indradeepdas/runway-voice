"""Question understanding, session memory, and answer composition.

Two layers:
1. A deterministic intent/scenario layer computes every number from the
   13-week cash engine. It carries session memory: follow-up questions
   inherit the previous intent, and "what if it slips further?" composes
   with the last scenario discussed.
2. An optional LLM layer (llm.py) re-phrases the computed answer when
   RUNWAY_LLM_API_KEY is configured. The LLM never computes numbers; on any
   failure the deterministic templates carry the answer alone.
"""
import copy
import re

import llm
from cash_model import load_company, summarize

SCENARIO_ALIASES = {
    "hire_engineer": ["hire", "engineer", "developer", "recruit"],
    "helios_pays_late": ["helios", "late", "delay", "pays late"],
    "lose_alba": ["alba", "lose", "churn", "falls through", "lost"],
    "cut_contractors": ["contractor", "freelance", "cut", "bench"],
}

INTENT_KEYWORDS = [
    ("runway", ["runway", "how long", "survive", "last"]),
    ("receivables", ["overdue", "receivable", "owed", "collect", "invoice"]),
    ("burn", ["burn", "spend", "cost", "expense"]),
    ("payables", ["payable", "owe", "vendor", "bill"]),
]

FURTHER_HINTS = ("more", "another", "further", "worse", "longer", "even")


def _contains_word(text, phrase):
    return re.search(r"\b" + re.escape(phrase) + r"\b", text) is not None


def detect_scenario(text):
    t = text.lower()
    for key, words in SCENARIO_ALIASES.items():
        if any(_contains_word(t, w) for w in words):
            return key
    return None


def detect_intent(text):
    q = text.lower()
    if detect_scenario(q):
        return "scenario"
    for intent, words in INTENT_KEYWORDS:
        if any(_contains_word(q, w) for w in words):
            return intent
    return None


def answer(question, company=None, history=None):
    """Answer a question. history is a list of (question, answer-dict) tuples
    from earlier in the session and drives follow-up memory."""
    company = company or load_company()
    history = history or []
    q = question.lower()
    base = summarize(company)

    intent = detect_intent(q)
    scenario_key = detect_scenario(q)
    followup_of = None

    if intent is None and history:
        # Session memory: inherit the previous topic for follow-ups.
        last_q, last_a = history[-1]
        intent = last_a.get("intent", "summary") if isinstance(last_a, dict) else "summary"
        scenario_key = last_a.get("scenario_key") if isinstance(last_a, dict) else None
        followup_of = last_q
        # Composition: "and if it slips even further?" doubles the last delay.
        if scenario_key == "helios_pays_late" and any(w in q for w in FURTHER_HINTS):
            company = copy.deepcopy(company)
            company["scenarios"]["helios_pays_late_x2"] = dict(
                company["scenarios"]["helios_pays_late"],
                delay_weeks=11,
                description="Helios Retail pays 11 weeks late (week 14 - outside the 13-week window)",
            )
            scenario_key = "helios_pays_late_x2"
            intent = "scenario"

    if intent == "scenario" and scenario_key:
        s = summarize(company, scenario_key)
        desc = company["scenarios"][scenario_key]["description"]
        delta = s["end_cash"] - base["end_cash"]
        runway_txt = (
            f"cash goes negative in week {s['runway_weeks']}"
            if s["runway_weeks"] else "cash stays positive across all 13 weeks"
        )
        text = (
            f"Scenario: {desc}. Week-13 cash would be EUR {s['end_cash']:,} "
            f"({'+' if delta >= 0 else ''}EUR {delta:,} vs. base), "
            f"lowest point EUR {s['min_cash']:,}, and {runway_txt}."
        )
        result = {"intent": "scenario", "scenario_key": scenario_key,
                  "text": text, "summary": s}
    elif intent == "runway":
        rw = base["runway_weeks"]
        txt = (
            f"Runway is under 13 weeks: cash goes negative in week {rw}. "
            f"That is the number to fix first."
            if rw else
            f"Cash stays positive for the full 13-week window. Lowest point is "
            f"EUR {base['min_cash']:,}; week-13 cash is EUR {base['end_cash']:,}."
        )
        result = {"intent": "runway", "text": txt, "summary": base}
    elif intent == "receivables":
        recs = company["receivables"]
        risky = [r for r in recs if r["probability"] < 0.9 or r["status"] != "confirmed"]
        total = sum(r["amount"] for r in recs)
        lines = [f"Open receivables total EUR {total:,}."]
        for r in risky:
            lines.append(
                f"{r['client']}: EUR {r['amount']:,} due week {r['due_week']} "
                f"at {int(r['probability']*100)}% confidence ({r['status'].replace('_',' ')})."
            )
        lines.append("Collecting Helios and Alba on time is worth more than any cost cut on the table.")
        result = {"intent": "receivables", "text": " ".join(lines), "summary": base}
    elif intent == "burn":
        fixed = company["weekly_fixed_costs"]
        top = sorted(fixed.items(), key=lambda kv: -kv[1])[:3]
        net = base["avg_weekly_burn"]
        net_txt = (
            f"Average weekly net burn is EUR {abs(net):,}."
            if net < 0 else
            f"The business is cash-generative: average weekly net inflow is EUR {net:,}."
        )
        txt = (
            net_txt + f" Fixed costs run EUR {sum(fixed.values()):,} per week; the big three are "
            + ", ".join(f"{k.replace('_',' ')} at EUR {v:,}" for k, v in top) + "."
        )
        result = {"intent": "burn", "text": txt, "summary": base}
    elif intent == "payables":
        pays = company["payables"]
        total = sum(p["amount"] for p in pays)
        nxt = min(pays, key=lambda p: p["due_week"])
        result = {
            "intent": "payables",
            "text": (
                f"Scheduled payables total EUR {total:,} over the quarter. "
                f"Next up: {nxt['vendor']}, EUR {nxt['amount']:,} in week {nxt['due_week']}. "
                f"The VAT prepayment in week 4 is the fixed date to plan around."
            ),
            "summary": base,
        }
    else:
        result = {
            "intent": "summary",
            "text": (
                f"Cash on hand is EUR {company['cash_on_hand']:,}. Over the next 13 weeks "
                f"the lowest point is EUR {base['min_cash']:,} and week-13 cash is "
                f"EUR {base['end_cash']:,}. Ask me about runway, receivables, payables, "
                f"burn, or run a scenario like hiring an engineer or losing Alba."
            ),
            "summary": base,
        }

    if followup_of:
        result["text"] = f"Following up on \"{followup_of}\": " + result["text"]
        result["followup_of"] = followup_of

    spoken = llm.narrate(
        question, result["text"], history,
        model_state=f"base week-13 cash EUR {base['end_cash']:,}, lowest point EUR {base['min_cash']:,}",
    )
    result["narrated_by"] = "llm" if spoken else "rules"
    if spoken:
        result["text"] = spoken
    return result
