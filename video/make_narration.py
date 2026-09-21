"""Generate per-slide narration audio with gTTS."""
from gtts import gTTS
from pathlib import Path

SEGMENTS = [
    ("01_title", "Runway Voice. Ask your cash flow anything. A voice-first cash copilot for small business founders, built on AssemblyAI."),
    ("02_problem", "Cash is the question founders ask most, and answer least. Cash-flow problems are the most-cited killer of small businesses. The numbers exist, but they sit in a spreadsheet the founder opens once a month. Existing FP&A tools are priced and built for finance teams. So the decisions that matter - hiring, pricing, collecting - get made on gut feel."),
    ("03_solution", "Runway Voice is a voice agent over a finance-grade thirteen-week cash model. Ask by voice: runway, burn, overdue invoices, vendor bills, and get the answer in seconds. Run what-if scenarios conversationally: hire someone, lose a client, a late payer. Every answer comes with the number, the trajectory, and the action that matters most."),
    ("04_architecture", "Here is how it works. The founder speaks. AssemblyAI Universal speech-to-text turns the question into text, handling accents, numbers, and company names. An intent and scenario engine routes the question to a direct-method thirteen-week cash model - the same methodology used in professional FP&A and turnaround work. The answer comes back with a cash chart."),
    ("05_demo_runway", "Let's see it live. The founder asks: what is our runway? Runway Voice answers from the model: cash stays positive for the full thirteen weeks. The lowest point is one hundred seventy-nine thousand euros, and week thirteen closes at two hundred twenty-eight thousand. One question, one second, one clear answer - with the chart to prove it."),
    ("06_demo_scenario", "Now a harder one: what happens if we hire an engineer? The scenario engine applies a senior hire at seven and a half thousand euros per week from week three. Week-thirteen cash drops by eighty-two and a half thousand to one hundred forty-six thousand - still positive, but the trajectory clearly bends. This is the difference between a spreadsheet and a conversation."),
    ("07_why_aai", "Why AssemblyAI? Universal speech-to-text handles founder-speak: accents, long numbers, unusual company names. Fast turnaround keeps the conversation at the speed of thought. And one API for the whole voice layer lets the product stay focused on the finance model. The streaming path is ready: the same engine works over Universal-Streaming for real-time Q&A."),
    ("08_business", "The business case. Hundreds of millions of small businesses worldwide share one universal pain: cash visibility. Enterprise FP&A suites start at thousands per month. Nothing serves the founder segment at twenty-nine euros a month. The wedge expands: accounting-ledger sync turns Q&A into a weekly voice brief, and retention is structural - the model compounds value as it learns each company's cash rhythm."),
    ("09_roadmap", "The roadmap. Today: voice Q&A and scenarios over the thirteen-week model - this submission. Next: live ledger and bank sync, replacing the demo dataset. Then: a proactive weekly voice brief - the copilot calls the founder before Monday. Later: multi-entity consolidation, and bilingual German and English voice."),
    ("10_close", "Runway Voice. Cash clarity at the speed of speech. Domain logic by a sixteen-year FP&A operator. Voice by AssemblyAI. Thank you."),
]

out = Path("video"); out.mkdir(exist_ok=True)
for name, text in SEGMENTS:
    gTTS(text=text, lang="en", tld="co.uk").save(out / f"{name}.mp3")
    print(f"{name} narrated")
