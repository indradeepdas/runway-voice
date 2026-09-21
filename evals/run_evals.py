"""Runway Voice eval harness - dependency-free, zero external API spend.

Usage: python3 evals/run_evals.py
Writes evals/RESULTS.md and exits non-zero on any failure.
"""
import os
import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.pop("RUNWAY_LLM_API_KEY", None)  # deterministic baseline

import brain
import voice
from cash_model import load_company, summarize

COMPANY = load_company()
BASE = summarize(COMPANY)
HIRE = summarize(COMPANY, "hire_engineer")

results = []


def check(name, condition, detail=""):
    results.append((name, bool(condition), detail))


# --- cash model invariants -------------------------------------------------
rows = BASE["rows"]
check("model: 13 weekly rows", len(rows) == 13)
check("model: week-13 = cash + sum(net)",
      rows[-1]["closing_cash"] == COMPANY["cash_on_hand"] + sum(r["net"] for r in rows))
check("model: hire scenario lowers week-13 by exactly EUR 82,500",
      BASE["end_cash"] - HIRE["end_cash"] == 82500,
      f"base {BASE['end_cash']:,} vs hire {HIRE['end_cash']:,}")

# --- intent routing ---------------------------------------------------------
a = brain.answer("What is our runway?", COMPANY)
check("intent: runway", a["intent"] == "runway")
check("runway answer carries real figures",
      f"{BASE['min_cash']:,}" in a["text"] and f"{BASE['end_cash']:,}" in a["text"], a["text"][:120])

a = brain.answer("Which invoices are overdue?", COMPANY)
check("intent: receivables", a["intent"] == "receivables")
check("receivables names risky clients", "Helios" in a["text"] and "Alba" in a["text"])

a = brain.answer("What is our weekly burn?", COMPANY)
check("intent: burn", a["intent"] == "burn")

a = brain.answer("What do we owe vendors?", COMPANY)
check("intent: payables", a["intent"] == "payables")
check("payables flags VAT week 4", "VAT" in a["text"] and "week 4" in a["text"])

a = brain.answer("What happens if we hire an engineer?", COMPANY)
check("intent: scenario (hire)", a["intent"] == "scenario" and a["scenario_key"] == "hire_engineer")
check("hire answer figures match model",
      f"{HIRE['end_cash']:,}" in a["text"] and "-82,500" in a["text"], a["text"][:160])

a = brain.answer("What if Helios pays late?", COMPANY)
check("intent: scenario (helios)", a["scenario_key"] == "helios_pays_late")

a = brain.answer("Tell me something unrelated to anything", COMPANY)
check("unknown question -> summary fallback", a["intent"] == "summary")

# --- session memory ---------------------------------------------------------
h = []
h.append(("What if Helios pays late?", brain.answer("What if Helios pays late?", COMPANY, h)))
fup = brain.answer("And if it slips even further?", COMPANY, h)
check("memory: follow-up inherits and compounds scenario",
      fup["scenario_key"] == "helios_pays_late_x2" and "Following up on" in fup["text"],
      fup["text"][:160])
single = summarize(COMPANY, "helios_pays_late")["end_cash"]
check("memory: compounded delay is strictly worse",
      fup["summary"]["end_cash"] < single,
      f"x2 {fup['summary']['end_cash']:,} vs single {single:,}")

h2 = [("What is our weekly burn?", brain.answer("What is our weekly burn?", COMPANY))]
fup2 = brain.answer("Tell me more about that", COMPANY, h2)
check("memory: generic follow-up inherits last intent",
      fup2["intent"] == "burn" and fup2.get("followup_of") == "What is our weekly burn?")

# --- LLM layer: safe fallback ----------------------------------------------
check("llm: no key -> rules narration", brain.answer("What is our runway?", COMPANY)["narrated_by"] == "rules")
os.environ["RUNWAY_LLM_API_KEY"] = "invalid-key-for-eval"
os.environ["RUNWAY_LLM_BASE_URL"] = "http://127.0.0.1:9/none"
b = brain.answer("What is our runway?", COMPANY)
check("llm: unreachable endpoint -> deterministic fallback still answers",
      b["narrated_by"] == "rules" and f"{BASE['end_cash']:,}" in b["text"])
os.environ.pop("RUNWAY_LLM_API_KEY"); os.environ.pop("RUNWAY_LLM_BASE_URL")

# --- voice layer ------------------------------------------------------------
os.environ.pop("ASSEMBLYAI_API_KEY", None)
check("voice: mock mode without key", voice.mode().startswith("mock"))
check("voice: mock transcript is canned", voice.transcribe() in voice.MOCK_TRANSCRIPTS)

# --- app end-to-end (Streamlit AppTest) -------------------------------------
try:
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(Path(__file__).resolve().parent.parent / "app.py"), default_timeout=30)
    at.run()
    check("app: boots without exception", not at.exception)
    at.text_input[0].set_value("What happens if we hire an engineer?")
    at.button[0].click().run()
    check("app: typed question answered exactly once",
          len(at.session_state["history"]) == 1 and "82,500" in at.session_state["history"][0][1]["text"])
    at.text_input[0].set_value("And if it slips even further?")
    at.button[0].click().run()
    hist = at.session_state["history"]
    check("app: follow-up uses session memory", len(hist) == 2 and hist[1][1].get("followup_of"))
    at.run()  # extra reruns must not duplicate answers
    at.run()
    check("app: reruns do not duplicate answers", len(at.session_state["history"]) == 2)
except Exception as e:  # AppTest unavailable in this environment
    check("app: AppTest e2e", False, f"skipped/failed: {e}")

# --- report -----------------------------------------------------------------
passed = sum(1 for _, ok, _ in results if ok)
lines = [
    "# Runway Voice - eval results",
    f"",
    f"Run: {datetime.datetime.now().isoformat(timespec='seconds')} (local, zero external API spend)",
    f"Result: {passed}/{len(results)} passed",
    "",
    "| # | Check | Result | Detail |",
    "|---|-------|--------|--------|",
]
for i, (name, ok, detail) in enumerate(results, 1):
    lines.append(f"| {i} | {name} | {'PASS' if ok else 'FAIL'} | {detail.replace('|', '/')} |")
out = Path(__file__).resolve().parent / "RESULTS.md"
out.write_text("\n".join(lines) + "\n")
print("\n".join(lines))
sys.exit(0 if passed == len(results) else 1)
