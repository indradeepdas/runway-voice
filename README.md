# Runway Voice

**Ask your cash flow anything.** A voice-first cash copilot for SMB founders, built on AssemblyAI.

Founders make hiring, pricing, and collection decisions on gut feel because the numbers sit in a spreadsheet they open once a month. Runway Voice puts a finance-grade 13-week cash model behind a voice interface: ask a question out loud, get the number, the trajectory, and the action that matters - in seconds.

## What it does

- **Voice Q&A** over a direct-method 13-week cash forecast: runway, burn, receivables, payables.
- **Conversational what-if scenarios**: hire an engineer, a client pays late, a deal falls through, cut contractors - with the cash trajectory re-computed instantly.
- **Answer + chart + action**: every response includes the week-13 cash position, the lowest point, and the one thing to fix first.

## Architecture

```
Founder's voice -> AssemblyAI Universal STT -> Intent & scenario engine -> 13-week cash model -> Answer + cash chart
```

- `voice.py` - AssemblyAI transcription layer (Universal model). Runs in **mock mode** when `ASSEMBLYAI_API_KEY` is not set, so the full pipeline works offline.
- `brain.py` - intent detection and answer composition (deterministic; the same contract an LLM router would fulfill).
- `cash_model.py` - direct-method 13-week forecast with probability-weighted receivables, fixed-cost cadence, discrete payables, and scenario overlays.
- `app.py` - Streamlit UI: mic input, typed fallback, trajectory chart, chat history.

## Run it

```bash
pip install -r requirements.txt
export ASSEMBLYAI_API_KEY=...   # optional; omit for mock mode
streamlit run app.py
```

## Demo data

`data/sample_company.json` is a **fictional** Berlin B2B consultancy. All figures are illustrative.

## Built for

AssemblyAI Voice Agent Hackathon (lablab.ai), September 2026.
Domain logic by a 16-year FP&A operator (PwC, Hilti, Delivery Hero). Voice by AssemblyAI.
