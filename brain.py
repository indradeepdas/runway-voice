"""Question understanding and answer composition over the cash model.

Rule-based intent layer (deterministic for demo reliability). In production the
transcript is handed to an LLM with the model state as context; the intent
layer below mirrors that contract 1:1.
"""
import re
from cash_model import load_company, summarize, forecast

SCENARIO_ALIASES = {
    "hire_engineer": ["hire", "engineer", "developer", "recruit"],
    "helios_pays_late": ["helios", "late", "delay", "pays late"],
    "lose_alba": ["alba", "lose", "churn", "falls through", "lost"],
    "cut_contractors": ["contractor", "freelance", "cut", "bench"],
}


def detect_scenario(text):
    t = text.lower()
    for key, words in SCENARIO_ALIASES.items():
        if any(w in t for w in words):
            return key
    return None


def answer(question, company=None):
    company = company or load_company()
    q = question.lower()
    base = summarize(company)

    if detect_scenario(q):
        key = detect_scenario(q)
        s = summarize(company, key)
        desc = company["scenarios"][key]["description"]
        delta = s["end_cash"] - base["end_cash"]
        runway_txt = (
            f"cash goes negative in week {s['runway_weeks']}"
            if s["runway_weeks"] else "cash stays positive across all 13 weeks"
        )
        return {
            "intent": "scenario",
            "scenario_key": key,
            "text": (
                f"Scenario: {desc}. Week-13 cash would be EUR {s['end_cash']:,} "
                f"({'+' if delta >= 0 else ''}EUR {delta:,} vs. base), "
                f"lowest point EUR {s['min_cash']:,}, and {runway_txt}."
            ),
            "summary": s,
        }

    if any(w in q for w in ["runway", "how long", "survive", "last"]):
        rw = base["runway_weeks"]
        txt = (
            f"Runway is under 13 weeks: cash goes negative in week {rw}. "
            f"That is the number to fix first."
            if rw else
            f"Cash stays positive for the full 13-week window. Lowest point is "
            f"EUR {base['min_cash']:,}; week-13 cash is EUR {base['end_cash']:,}."
        )
        return {"intent": "runway", "text": txt, "summary": base}

    if any(w in q for w in ["overdue", "receivable", "owed", "collect", "invoice"]):
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
        return {"intent": "receivables", "text": " ".join(lines), "summary": base}

    if any(w in q for w in ["burn", "spend", "cost", "expense"]):
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
        return {"intent": "burn", "text": txt, "summary": base}

    if any(w in q for w in ["payable", "owe", "vendor", "bill"]):
        pays = company["payables"]
        total = sum(p["amount"] for p in pays)
        nxt = min(pays, key=lambda p: p["due_week"])
        return {
            "intent": "payables",
            "text": (
                f"Scheduled payables total EUR {total:,} over the quarter. "
                f"Next up: {nxt['vendor']}, EUR {nxt['amount']:,} in week {nxt['due_week']}. "
                f"The VAT prepayment in week 4 is the fixed date to plan around."
            ),
            "summary": base,
        }

    return {
        "intent": "summary",
        "text": (
            f"Cash on hand is EUR {company['cash_on_hand']:,}. Over the next 13 weeks "
            f"the lowest point is EUR {base['min_cash']:,} and week-13 cash is "
            f"EUR {base['end_cash']:,}. Ask me about runway, receivables, payables, "
            f"burn, or run a scenario like hiring an engineer or losing Alba."
        ),
        "summary": base,
    }
