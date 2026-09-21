"""13-week rolling cash-flow engine with scenario overlays.

Methodology mirrors the standard direct-method 13-week cash forecast used in
FP&A and turnaround practice: weekly granularity, probability-weighted
receivables, fixed-cost cadence, and discrete payable events.
"""
import copy
import json
from pathlib import Path

WEEKS = 13


def load_company(path=None):
    path = path or Path(__file__).parent / "data" / "sample_company.json"
    with open(path) as f:
        return json.load(f)


def apply_scenario(company, scenario_key):
    """Return a modified copy of the company with the scenario applied."""
    c = copy.deepcopy(company)
    sc = c["scenarios"].get(scenario_key)
    if not sc:
        return c
    if "delay_client" in sc:
        for r in c["receivables"]:
            if r["client"] == sc["delay_client"]:
                r["due_week"] += sc["delay_weeks"]
                r["probability"] = max(0.5, r["probability"] - 0.15)
    if "remove_client" in sc:
        c["receivables"] = [r for r in c["receivables"] if r["client"] != sc["remove_client"]]
    return c


def forecast(company, scenario_key=None):
    """Build the 13-week forecast. Returns list of weekly dicts."""
    c = apply_scenario(company, scenario_key) if scenario_key else copy.deepcopy(company)
    sc = c["scenarios"].get(scenario_key, {}) if scenario_key else {}

    fixed = sum(c["weekly_fixed_costs"].values())
    rows = []
    cash = c["cash_on_hand"]
    for w in range(1, WEEKS + 1):
        inflows = c["recurring_revenue_weekly"]
        inflows += sum(
            r["amount"] * r["probability"]
            for r in c["receivables"] if r["due_week"] == w
        )
        outflows = fixed
        outflows += sum(p["amount"] for p in c["payables"] if p["due_week"] == w)
        if sc.get("weekly_cost_delta") and w >= sc.get("start_week", 1):
            outflows -= sc["weekly_cost_delta"]  # negative delta = extra cost
        net = inflows - outflows
        cash += net
        rows.append({
            "week": w,
            "inflows": round(inflows),
            "outflows": round(outflows),
            "net": round(net),
            "closing_cash": round(cash),
        })
    return rows


def runway_weeks(rows):
    """Weeks until closing cash goes negative (None if it never does in window)."""
    for r in rows:
        if r["closing_cash"] < 0:
            return r["week"]
    return None


def min_cash(rows):
    return min(r["closing_cash"] for r in rows)


def summarize(company, scenario_key=None):
    rows = forecast(company, scenario_key)
    return {
        "scenario": scenario_key or "base",
        "rows": rows,
        "runway_weeks": runway_weeks(rows),
        "min_cash": min_cash(rows),
        "end_cash": rows[-1]["closing_cash"],
        "avg_weekly_burn": round(sum(r["net"] for r in rows) / len(rows)),
    }
