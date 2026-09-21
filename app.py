"""Runway Voice - a voice-first cash copilot for SMB founders.

Ask by voice or text: runway, receivables, payables, burn, and what-if
scenarios over a direct-method 13-week cash forecast. Built on AssemblyAI
Universal speech-to-text.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st

from brain import answer
from cash_model import load_company, summarize
from voice import transcribe, mode

st.set_page_config(page_title="Runway Voice", page_icon="🎙️", layout="wide")

COMPANY = load_company()

st.title("Runway Voice")
st.caption(f"Ask your 13-week cash forecast anything - by voice. Speech-to-text: {mode()}.")

with st.sidebar:
    st.header("Demo company")
    st.metric("Cash on hand", f"EUR {COMPANY['cash_on_hand']:,}")
    base = summarize(COMPANY)
    st.metric("Lowest point (13 wks)", f"EUR {base['min_cash']:,}")
    st.metric("Week-13 cash", f"EUR {base['end_cash']:,}")
    st.divider()
    st.markdown("**Try asking**")
    for q in ["What is our runway?", "Which invoices are overdue?",
              "What happens if we hire an engineer?", "What if Helios pays late?",
              "What is our weekly burn?", "What do we owe vendors?"]:
        st.markdown(f"- {q}")

if "history" not in st.session_state:
    st.session_state.history = []

col_in, col_out = st.columns([1, 1])

with col_in:
    st.subheader("Ask")
    audio = st.audio_input("Record a question") if hasattr(st, "audio_input") else None
    typed = st.text_input("...or type it", placeholder="What happens if we hire an engineer?")
    asked = None
    if audio is not None:
        with open("/tmp/rv_question.wav", "wb") as f:
            f.write(audio.read())
        asked = transcribe("/tmp/rv_question.wav")
        st.info(f"Heard: {asked}")
    elif typed:
        asked = typed

    if asked:
        with st.spinner("Thinking over your 13-week model..."):
            st.session_state.history.append((asked, answer(asked, COMPANY)))

with col_out:
    st.subheader("13-week cash trajectory")
    s = base if not st.session_state.history else st.session_state.history[-1][1]["summary"]
    fig, ax = plt.subplots(figsize=(7, 3.6))
    weeks = [r["week"] for r in s["rows"]]
    cash = [r["closing_cash"] for r in s["rows"]]
    ax.plot(weeks, cash, marker="o", color="#1a5d3a", label=f"Scenario: {s['scenario']}")
    base_rows = summarize(COMPANY)["rows"]
    if s["scenario"] != "base":
        ax.plot(weeks, [r["closing_cash"] for r in base_rows], marker=".",
                color="#888", linestyle="--", label="Base")
    ax.axhline(0, color="#b00020", linewidth=1)
    ax.set_xlabel("Week"); ax.set_ylabel("Closing cash (EUR)")
    ax.legend(); ax.grid(alpha=0.25)
    st.pyplot(fig)

for q, a in reversed(st.session_state.history):
    with st.chat_message("user"):
        st.write(q)
    with st.chat_message("assistant"):
        st.write(a["text"])
