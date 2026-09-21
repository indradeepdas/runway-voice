# Runway Voice - eval results

Run: 2026-09-21T19:26:05 (local, zero external API spend)
Result: 25/25 passed

| # | Check | Result | Detail |
|---|-------|--------|--------|
| 1 | model: 13 weekly rows | PASS |  |
| 2 | model: week-13 = cash + sum(net) | PASS |  |
| 3 | model: hire scenario lowers week-13 by exactly EUR 82,500 | PASS | base 228,415 vs hire 145,915 |
| 4 | intent: runway | PASS |  |
| 5 | runway answer carries real figures | PASS | Cash stays positive for the full 13-week window. Lowest point is EUR 179,130; week-13 cash is EUR 228,415. |
| 6 | intent: receivables | PASS |  |
| 7 | receivables names risky clients | PASS |  |
| 8 | intent: burn | PASS |  |
| 9 | intent: payables | PASS |  |
| 10 | payables flags VAT week 4 | PASS |  |
| 11 | intent: scenario (hire) | PASS |  |
| 12 | hire answer figures match model | PASS | Scenario: Hire one senior engineer at EUR 7,500/week fully loaded, starting week 3. Week-13 cash would be EUR 145,915 (EUR -82,500 vs. base), lowest point EUR 1 |
| 13 | intent: scenario (helios) | PASS |  |
| 14 | unknown question -> summary fallback | PASS |  |
| 15 | memory: follow-up inherits and compounds scenario | PASS | Following up on "What if Helios pays late?": Scenario: Helios Retail pays 11 weeks late (week 14 - outside the 13-week window). Week-13 cash would be EUR 205,61 |
| 16 | memory: compounded delay is strictly worse | PASS | x2 205,615 vs single 224,140 |
| 17 | memory: generic follow-up inherits last intent | PASS |  |
| 18 | llm: no key -> rules narration | PASS |  |
| 19 | llm: unreachable endpoint -> deterministic fallback still answers | PASS |  |
| 20 | voice: mock mode without key | PASS |  |
| 21 | voice: mock transcript is canned | PASS |  |
| 22 | app: boots without exception | PASS |  |
| 23 | app: typed question answered exactly once | PASS |  |
| 24 | app: follow-up uses session memory | PASS |  |
| 25 | app: reruns do not duplicate answers | PASS |  |
