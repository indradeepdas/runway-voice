"""Generate cover, slide PNGs, slides.pdf, narration audio, and demo video frames."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import textwrap, subprocess

from cash_model import load_company, summarize

W, H = 1280, 720
OUT = Path("slides"); OUT.mkdir(exist_ok=True)
BG = "#0e2a1f"; PANEL = "#153527"; ACCENT = "#4ade80"; WHITE = "#f2f7f4"; GREY = "#9fb8aa"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def f(sz, bold=False): return ImageFont.truetype(FONTB if bold else FONT, sz)

COMPANY = load_company()
BASE = summarize(COMPANY)
SCEN = summarize(COMPANY, "hire_engineer")

def chart_png(path, scenario=None, small=False):
    rows = (scenario or BASE)["rows"]
    fig, ax = plt.subplots(figsize=(6.4, 3.4) if small else (8, 4.2), dpi=150)
    fig.patch.set_facecolor("#153527"); ax.set_facecolor("#153527")
    ax.plot([r["week"] for r in rows], [r["closing_cash"] for r in rows],
            marker="o", color="#4ade80", linewidth=2.5, label=(scenario or BASE)["scenario"])
    if scenario:
        ax.plot([r["week"] for r in BASE["rows"]], [r["closing_cash"] for r in BASE["rows"]],
                linestyle="--", color="#9fb8aa", label="base")
    ax.axhline(0, color="#ff6b6b", linewidth=1)
    ax.tick_params(colors="#9fb8aa"); ax.set_xlabel("week", color="#9fb8aa")
    ax.set_ylabel("closing cash (EUR)", color="#9fb8aa")
    for s in ax.spines.values(): s.set_color("#2c5743")
    ax.legend(facecolor="#153527", labelcolor="#f2f7f4")
    ax.grid(alpha=0.15, color="#9fb8aa")
    plt.tight_layout(); fig.savefig(path, facecolor="#153527"); plt.close(fig)

chart_png("assets/chart_base.png")
chart_png("assets/chart_scenario.png", SCEN)

def new_slide():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, H-14, W, H], fill=ACCENT)
    return img, d

def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

def bullets(d, items, x, y, size=30, gap=58, color=WHITE, maxw=1050):
    for it in items:
        d.ellipse([x, y+12, x+12, y+24], fill=ACCENT)
        for ln in wrap(d, it, f(size), maxw):
            d.text((x+30, y), ln, font=f(size), fill=color); y += size + 10
        y += gap - size - 10
    return y

def header(d, txt, sub=None):
    d.text((70, 48), txt, font=f(46, True), fill=WHITE)
    if sub: d.text((70, 112), sub, font=f(24), fill=GREY)
    d.line([70, 155 if sub else 130, W-70, 155 if sub else 130], fill="#2c5743", width=2)

slides = []

# 1 title
img, d = new_slide()
d.text((70, 200), "Runway Voice", font=f(96, True), fill=WHITE)
d.text((70, 330), "Ask your cash flow anything.", font=f(44), fill=ACCENT)
d.text((70, 420), "A voice-first cash copilot for SMB founders, built on AssemblyAI.", font=f(28), fill=GREY)
d.text((70, 600), "AssemblyAI Voice Agent Hackathon - September 2026", font=f(24), fill=GREY)
slides.append(("01_title", img))

# 2 problem
img, d = new_slide(); header(d, "The problem", "Cash is the question founders ask most - and answer least")
bullets(d, [
    "Cash-flow problems are the most-cited killer of small businesses (U.S. Bank study: 82% of failures).",
    "The numbers exist - but they sit in a spreadsheet the founder opens once a month.",
    "Existing FP&A tools are priced and built for finance teams, not for a founder between meetings.",
    "The result: hiring, pricing and payment decisions get made on gut feel.",
], 70, 210)
slides.append(("02_problem", img))

# 3 solution
img, d = new_slide(); header(d, "The solution", "A voice agent over a finance-grade 13-week cash model")
bullets(d, [
    "Ask by voice: runway, burn, overdue invoices, vendor bills - answered in seconds.",
    "Run what-if scenarios conversationally: hire, lose a client, a late payer, cost cuts.",
    "Under the hood: the direct-method 13-week forecast used in professional FP&A and turnaround work.",
    "Every answer comes with the number, the trajectory, and the action that matters most.",
], 70, 210)
slides.append(("03_solution", img))

# 4 architecture
img, d = new_slide(); header(d, "How it works", "Voice in, decision out")
boxes = [("Founder's", "voice", "mic"), ("AssemblyAI", "Universal STT", "speech to text"),
         ("Intent &", "scenario engine", "question routing"), ("13-week", "cash model", "direct method"),
         ("Answer +", "cash chart", "number + action")]
x = 55
for i, (t1, t2, s) in enumerate(boxes):
    d.rounded_rectangle([x, 300, x+200, 460], 18, fill=PANEL, outline="#2c5743", width=2)
    d.text((x+100, 348), t1, font=f(21, True), fill=WHITE, anchor="mm")
    d.text((x+100, 376), t2, font=f(21, True), fill=WHITE, anchor="mm")
    d.text((x+100, 428), s, font=f(15), fill=GREY, anchor="mm")
    if i < 4:
        d.line([x+202, 380, x+234, 380], fill=ACCENT, width=4)
        d.polygon([(x+236, 380), (x+222, 372), (x+222, 388)], fill=ACCENT)
    x += 245
slides.append(("04_architecture", img))

# 5-6 demo frames
def demo_slide(name, question, answer_text, chart):
    img, d = new_slide(); header(d, "Live demo", "Real questions, real numbers (fictional demo company)")
    d.rounded_rectangle([70, 195, 1210, 285], 16, fill="#1d4636")
    d.text((95, 228), "Q:  " + question, font=f(28, True), fill=WHITE)
    d.rounded_rectangle([70, 305, 1210, 620], 16, fill=PANEL, outline="#2c5743", width=2)
    d.text((95, 335), "A:", font=f(24, True), fill=ACCENT)
    y = 375
    for ln in wrap(d, answer_text, f(24), 600):
        d.text((95, y), ln, font=f(24), fill=WHITE); y += 38
    ch = Image.open(chart); ch.thumbnail((460, 460))
    img.paste(ch, (745, 320))
    slides.append((name, img))

from brain import answer as brains_answer
a1 = brains_answer("What is our runway?", COMPANY)
demo_slide("05_demo_runway", "What is our runway?", a1["text"], "assets/chart_base.png")
a2 = brains_answer("What happens if we hire an engineer?", COMPANY)
demo_slide("06_demo_scenario", "What happens if we hire an engineer?", a2["text"], "assets/chart_scenario.png")

# 7 why assemblyai
img, d = new_slide(); header(d, "Why AssemblyAI", "The voice layer this use case needs")
bullets(d, [
    "Universal speech-to-text handles founder-speak: accents, numbers, company names.",
    "Fast turnaround keeps the conversation at the speed of thought - no typing, no menus.",
    "One API for the whole voice layer lets the product stay focused on the finance model.",
    "Streaming path is ready: the same intent engine works over Universal-Streaming for real-time Q&A.",
], 70, 210)
slides.append(("07_why_aai", img))

# 8 business value
img, d = new_slide(); header(d, "Business value", "A wedge into the SMB finance stack")
bullets(d, [
    "400M+ small businesses worldwide; cash visibility is their most universal pain.",
    "Enterprise FP&A suites start at thousands per month - nothing serves the founder segment at EUR 29/mo.",
    "Wedge expansion: accounting-ledger sync (DATEV, Xero, QuickBooks) turns Q&A into a weekly voice brief.",
    "Retention is structural: the model compounds value as it learns each company's cash rhythm.",
], 70, 210)
slides.append(("08_business", img))

# 9 roadmap
img, d = new_slide(); header(d, "Roadmap", "From demo to daily habit")
bullets(d, [
    "Now: voice Q&A + scenarios over a 13-week model (this submission).",
    "Next: live ledger and bank sync, replacing the demo dataset.",
    "Then: proactive weekly voice brief - the copilot calls the founder before Monday.",
    "Later: multi-entity consolidation and German/English bilingual voice.",
], 70, 210)
slides.append(("09_roadmap", img))

# 10 close
img, d = new_slide()
d.text((70, 230), "Cash clarity at the speed of speech.", font=f(52, True), fill=WHITE)
d.text((70, 330), "Domain logic by a 16-year FP&A operator (PwC, Hilti, Delivery Hero).", font=f(26), fill=GREY)
d.text((70, 375), "Voice by AssemblyAI. Built for the AssemblyAI Voice Agent Hackathon 2026.", font=f(26), fill=GREY)
d.text((70, 470), "Runway Voice", font=f(40, True), fill=ACCENT)
slides.append(("10_close", img))

paths = []
for name, img in slides:
    p = OUT / f"{name}.png"; img.save(p); paths.append(p)

# cover image (16:9)
slides[0][1].save("assets/cover.png")

# slides.pdf
imgs = [Image.open(p).convert("RGB") for p in paths]
imgs[0].save("slides/RunwayVoice_slides.pdf", save_all=True, append_images=imgs[1:])
print(f"{len(paths)} slides + cover + PDF done")
