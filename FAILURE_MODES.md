# Runway Voice - known failure modes (working draft)

1. Mic-less environments: voice input needs a microphone and browser permission. Mitigation: full typed-input fallback with the same engine.
2. STT number errors: long spoken numbers and unusual company names can transcribe wrong. Mitigation: the app echoes the parsed figures before computing; user corrects by voice or text.
3. Demo-data boundary: the model runs on a fictional company dataset; it does not read the user's real books yet. Stated in the UI and docs.
4. Out-of-scope questions: non-cash questions (tax advice, legal) are routed to a fixed refusal, not improvised.
5. Scenario assumptions: what-if answers depend on stated assumptions (e.g., hire cost per week); the app shows the assumption next to the result.
6. Single-user, single-entity: no multi-entity consolidation or auth; stated on the roadmap, not hidden.
