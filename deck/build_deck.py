import json, subprocess, sys

PID = "14ZWoW8QQS87tRKQobLRjxOl88MpwnN6MngY_ts_abz0"
ACC = "indradeep.das@gmail.com"
EMU = 914400  # per inch
PAGE_W, PAGE_H = 9144000, 5143500

BG     = {"red":0.055,"green":0.165,"blue":0.122}
PANEL  = {"red":0.082,"green":0.208,"blue":0.153}
ACCENT = {"red":0.290,"green":0.871,"blue":0.502}
WHITE  = {"red":0.949,"green":0.969,"blue":0.957}
GREY   = {"red":0.624,"green":0.722,"blue":0.667}
BORDER = {"red":0.173,"green":0.341,"blue":0.263}
BUBBLE = {"red":0.114,"green":0.275,"blue":0.212}

def E(v): return {"magnitude": v, "unit": "EMU"}
def IN(v): return int(v * EMU)
def solid(c): return {"solidFill": {"color": {"rgbColor": c}, "alpha": 1}}

def bg_req(sid):
    return {"updatePageProperties": {"objectId": sid,
        "pageProperties": {"pageBackgroundFill": solid(BG)},
        "fields": "pageBackgroundFill"}}

def shape(oid, sid, stype, x, y, w, h):
    return {"createShape": {"objectId": oid, "shapeType": stype,
        "elementProperties": {"pageObjectId": sid,
            "size": {"width": E(IN(w)), "height": E(IN(h))},
            "transform": {"scaleX":1,"scaleY":1,"translateX":IN(x),"translateY":IN(y),"unit":"EMU"}}}}

def fill(oid, color, outline_color=None):
    props = {"shapeBackgroundFill": solid(color)}
    if outline_color is None:
        props["outline"] = {"propertyState": "NOT_RENDERED"}
        fields = "shapeBackgroundFill,outline"
    else:
        props["outline"] = {"outlineFill": solid(outline_color), "weight": {"magnitude": 1, "unit": "PT"}}
        fields = "shapeBackgroundFill,outline"
    return {"updateShapeProperties": {"objectId": oid, "shapeProperties": props, "fields": fields}}

def text(oid, txt):
    return {"insertText": {"objectId": oid, "text": txt, "insertionIndex": 0}}

def tstyle(oid, size, color, bold=False, font="Arial"):
    return {"updateTextStyle": {"objectId": oid, "textRange": {"type": "ALL"},
        "style": {"fontSize": {"magnitude": size, "unit": "PT"}, "fontFamily": font,
                  "bold": bold, "foregroundColor": {"opaqueColor": {"rgbColor": color}}},
        "fields": "fontSize,fontFamily,bold,foregroundColor"}}

def align(oid, a="CENTER"):
    return {"updateParagraphStyle": {"objectId": oid, "textRange": {"type": "ALL"},
        "style": {"alignment": a}, "fields": "alignment"}}

def bullets_style(oid, space=12):
    return [
        {"createParagraphBullets": {"objectId": oid, "textRange": {"type": "ALL"}, "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}},
        {"updateParagraphStyle": {"objectId": oid, "textRange": {"type": "ALL"},
            "style": {"spaceBelow": {"magnitude": space, "unit": "PT"}, "lineSpacing": 115},
            "fields": "spaceBelow,lineSpacing"}},
    ]

def image(oid, sid, url, x, y, w, h):
    return {"createImage": {"objectId": oid, "url": url,
        "elementProperties": {"pageObjectId": sid,
            "size": {"width": E(IN(w)), "height": E(IN(h))},
            "transform": {"scaleX":1,"scaleY":1,"translateX":IN(x),"translateY":IN(y),"unit":"EMU"}}}}

def bottom_bar(sid):
    return [shape(f"{sid}_bar", sid, "RECTANGLE", 0, 5.55, 10, 0.075),
            fill(f"{sid}_bar", ACCENT)]

def header(sid, title, sub=None):
    r = [shape(f"{sid}_t", sid, "TEXT_BOX", 0.55, 0.28, 8.9, 0.6), text(f"{sid}_t", title), tstyle(f"{sid}_t", 28, WHITE, True)]
    y = 0.9
    if sub:
        r += [shape(f"{sid}_s", sid, "TEXT_BOX", 0.55, y, 8.9, 0.4), text(f"{sid}_s", sub), tstyle(f"{sid}_s", 14, GREY)]
        y += 0.45
    r += [shape(f"{sid}_div", sid, "RECTANGLE", 0.55, y+0.12, 8.9, 0.015), fill(f"{sid}_div", BORDER)]
    return r

def bullet_box(sid, items, y=1.65, h=3.6, size=14):
    txt = "\n".join(items)
    r = [shape(f"{sid}_b", sid, "TEXT_BOX", 0.6, y, 8.8, h), text(f"{sid}_b", txt), tstyle(f"{sid}_b", size, WHITE)]
    r += bullets_style(f"{sid}_b")
    return r

def slide_reqs(i, builder):
    sid = f"slide{i:02d}"
    reqs = [{"createSlide": {"objectId": sid, "slideLayoutReference": {"predefinedLayout": "BLANK"}}}, bg_req(sid)]
    reqs += builder(sid)
    reqs += bottom_bar(sid)
    return reqs

# --- slide builders ---
def s_title(sid):
    return [
        shape(f"{sid}_1", sid, "TEXT_BOX", 0.55, 1.5, 8.9, 1.1), text(f"{sid}_1", "Runway Voice"), tstyle(f"{sid}_1", 60, WHITE, True),
        shape(f"{sid}_2", sid, "TEXT_BOX", 0.55, 2.75, 8.9, 0.6), text(f"{sid}_2", "Ask your cash flow anything."), tstyle(f"{sid}_2", 28, ACCENT),
        shape(f"{sid}_3", sid, "TEXT_BOX", 0.55, 3.55, 8.9, 0.4), text(f"{sid}_3", "A voice-first cash copilot for SMB founders, built on AssemblyAI."), tstyle(f"{sid}_3", 16, GREY),
        shape(f"{sid}_4", sid, "TEXT_BOX", 0.55, 4.9, 8.9, 0.35), text(f"{sid}_4", "AssemblyAI Voice Agent Hackathon - September 2026"), tstyle(f"{sid}_4", 12, GREY),
    ]

def s_problem(sid):
    return header(sid, "The problem", "Cash is the question founders ask most - and answer least") + bullet_box(sid, [
        "Cash-flow problems are the most-cited killer of small businesses (U.S. Bank study: 82% of failures).",
        "The numbers exist - but they sit in a spreadsheet the founder opens once a month.",
        "Existing FP&A tools are priced and built for finance teams, not for a founder between meetings.",
        "The result: hiring, pricing and payment decisions get made on gut feel.",
    ])

def s_solution(sid):
    return header(sid, "The solution", "A voice agent over a finance-grade 13-week cash model") + bullet_box(sid, [
        "Ask by voice: runway, burn, overdue invoices, vendor bills - answered in seconds.",
        "Run what-if scenarios conversationally: hire, lose a client, a late payer, cost cuts.",
        "Under the hood: the direct-method 13-week forecast used in professional FP&A and turnaround work.",
        "Every answer comes with the number, the trajectory, and the action that matters most.",
    ])

def s_arch(sid):
    boxes = [("Founder's\nvoice", "mic"), ("AssemblyAI\nUniversal STT", "speech to text"),
             ("Intent &\nscenario engine", "question routing"), ("13-week\ncash model", "direct method"),
             ("Answer +\ncash chart", "number + action")]
    r = header(sid, "How it works", "Voice in, decision out")
    x = 0.45
    for i, (t, c) in enumerate(boxes):
        oid = f"{sid}_bx{i}"
        r += [shape(oid, sid, "ROUND_RECTANGLE", x, 2.35, 1.6, 1.15), fill(oid, PANEL, BORDER)]
        tid = f"{sid}_bx{i}t"
        r += [shape(tid, sid, "TEXT_BOX", x+0.05, 2.55, 1.5, 0.6), text(tid, t), tstyle(tid, 10, WHITE, True), align(tid)]
        cid = f"{sid}_bx{i}c"
        r += [shape(cid, sid, "TEXT_BOX", x+0.05, 3.18, 1.5, 0.3), text(cid, c), tstyle(cid, 8, GREY), align(cid)]
        if i < 4:
            aid = f"{sid}_ar{i}"
            r += [shape(aid, sid, "TEXT_BOX", x+1.62, 2.68, 0.32, 0.4), text(aid, ">"), tstyle(aid, 18, ACCENT, True), align(aid)]
        x += 1.92
    return r

def demo(sid, q, a, chart_url):
    return header(sid, "Live demo", "Real questions, real numbers (fictional demo company)") + [
        shape(f"{sid}_q", sid, "ROUND_RECTANGLE", 0.55, 1.55, 8.9, 0.62), fill(f"{sid}_q", BUBBLE),
        shape(f"{sid}_qt", sid, "TEXT_BOX", 0.75, 1.68, 8.5, 0.4), text(f"{sid}_qt", "Q:  " + q), tstyle(f"{sid}_qt", 15, WHITE, True),
        shape(f"{sid}_a", sid, "ROUND_RECTANGLE", 0.55, 2.35, 8.9, 2.5), fill(f"{sid}_a", PANEL, BORDER),
        shape(f"{sid}_at", sid, "TEXT_BOX", 0.75, 2.55, 5.0, 2.1), text(f"{sid}_at", "A:  " + a), tstyle(f"{sid}_at", 12, WHITE),
        image(f"{sid}_ch", sid, chart_url, 5.95, 2.55, 3.3, 1.86),
    ]

RUNWAY_A = "Cash stays positive for the full 13-week window. Lowest point is EUR 179,130; week-13 cash is EUR 228,415."
SCEN_A = ("Scenario: Hire one senior engineer at EUR 7,500/week fully loaded, starting week 3. "
          "Week-13 cash would be EUR 145,915 (EUR -82,500 vs. base), lowest point EUR 145,915, and cash stays positive across all 13 weeks.")
CHART_BASE = "https://raw.githubusercontent.com/indradeepdas/runway-voice/main/assets/chart_base.png"
CHART_SCEN = "https://raw.githubusercontent.com/indradeepdas/runway-voice/main/assets/chart_scenario.png"

def s_demo1(sid): return demo(sid, "What is our runway?", RUNWAY_A, CHART_BASE)
def s_demo2(sid): return demo(sid, "What happens if we hire an engineer?", SCEN_A, CHART_SCEN)

def s_why(sid):
    return header(sid, "Why AssemblyAI", "The voice layer this use case needs") + bullet_box(sid, [
        "Universal speech-to-text handles founder-speak: accents, numbers, company names.",
        "Fast turnaround keeps the conversation at the speed of thought - no typing, no menus.",
        "One API for the whole voice layer lets the product stay focused on the finance model.",
        "Streaming path is ready: the same intent engine works over Universal-Streaming for real-time Q&A.",
    ])

def s_biz(sid):
    return header(sid, "Business value", "A wedge into the SMB finance stack") + bullet_box(sid, [
        "400M+ small businesses worldwide; cash visibility is their most universal pain.",
        "Enterprise FP&A suites start at thousands per month - nothing serves the founder segment at EUR 29/mo.",
        "Wedge expansion: accounting-ledger sync (DATEV, Xero, QuickBooks) turns Q&A into a weekly voice brief.",
        "Retention is structural: the model compounds value as it learns each company's cash rhythm.",
    ])

def s_road(sid):
    return header(sid, "Roadmap", "From demo to daily habit") + bullet_box(sid, [
        "Now: voice Q&A + scenarios over a 13-week model (this submission).",
        "Next: live ledger and bank sync, replacing the demo dataset.",
        "Then: proactive weekly voice brief - the copilot calls the founder before Monday.",
        "Later: multi-entity consolidation and German/English bilingual voice.",
    ])

def s_close(sid):
    return [
        shape(f"{sid}_1", sid, "TEXT_BOX", 0.55, 1.85, 8.9, 0.8), text(f"{sid}_1", "Cash clarity at the speed of speech."), tstyle(f"{sid}_1", 32, WHITE, True),
        shape(f"{sid}_2", sid, "TEXT_BOX", 0.55, 2.85, 8.9, 0.7), text(f"{sid}_2", "Domain logic by a 16-year FP&A operator (PepsiCo, Hilti, Delivery Hero).\nVoice by AssemblyAI. Built for the AssemblyAI Voice Agent Hackathon 2026."), tstyle(f"{sid}_2", 14, GREY),
        shape(f"{sid}_3", sid, "TEXT_BOX", 0.55, 3.9, 8.9, 0.55), text(f"{sid}_3", "Runway Voice"), tstyle(f"{sid}_3", 24, ACCENT, True),
    ]

BUILDERS = [s_title, s_problem, s_solution, s_arch, s_demo1, s_demo2, s_why, s_biz, s_road, s_close]

def call(reqs):
    p = subprocess.run(["tools", "google-slides", "batch-update", "--account-id", ACC,
                        "--presentation-id", PID, "--requests", json.dumps(reqs), "--json"],
                       capture_output=True, text=True, timeout=120)
    if p.returncode != 0:
        print("FAIL:", p.stderr[:800] or p.stdout[:800]); sys.exit(1)
    out = json.loads(p.stdout)
    print("ok:", out.get("mutation", {}).get("reply_count"), "requests applied")

# get existing first slide to delete later
p = subprocess.run(["tools", "google-slides", "get-presentation", "--account-id", ACC,
                    "--presentation-id", PID, "--json"], capture_output=True, text=True, timeout=60)
pres = json.loads(p.stdout)
orig = pres["presentation"]["slides"][0]["object_id"]
print("original slide:", orig)

for i, b in enumerate(BUILDERS, start=1):
    print(f"slide {i}...", end=" ")
    call(slide_reqs(i, b))

call([{"deleteObject": {"objectId": orig}}])
print("deck complete:", f"https://docs.google.com/presentation/d/{PID}/edit")
