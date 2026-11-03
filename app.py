import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
from ddgs import DDGS

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-3.5-flash-lite")

st.set_page_config(page_title="ReAct Agent", page_icon="🔎", layout="wide")

VIOLET = "#7C5CFF"
TEAL = "#00E5C7"
BG = "#0A0A16"

# ---------------------------------------------------------------------------
# STYLING
# ---------------------------------------------------------------------------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=JetBrains+Mono:wght@400;500&family=Inter:wght@400;500;600&display=swap');

html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
    background-color: {BG} !important;
    font-family: 'Inter', sans-serif;
}}

/* ---------- Animated 3D-ish rotating color wash ---------- */
.mesh-layer {{
    position: fixed;
    top: -20%; left: -20%;
    width: 140%; height: 140%;
    pointer-events: none;
    z-index: 0;
    background: conic-gradient(from 0deg at 50% 50%,
        rgba(124,92,255,0.22), rgba(0,229,199,0.18), rgba(124,92,255,0.10),
        rgba(0,229,199,0.22), rgba(124,92,255,0.22));
    filter: blur(80px);
    animation: rotateMesh 40s linear infinite;
}}

@keyframes rotateMesh {{
    from {{ transform: rotate(0deg); }}
    to {{ transform: rotate(360deg); }}
}}

.vignette {{
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 0;
    background: radial-gradient(circle at 50% 40%, transparent 35%, rgba(5,5,12,0.75) 100%);
}}

/* side decorative beams to fill empty gutters on wide screens */
.side-beam {{
    position: fixed;
    top: 0;
    width: 2px;
    height: 100%;
    z-index: 0;
    opacity: 0.35;
    background: linear-gradient(180deg, transparent, {TEAL}, transparent);
    animation: beamPulse 5s ease-in-out infinite;
}}
.side-beam.left {{ left: 4%; }}
.side-beam.right {{ right: 4%; background: linear-gradient(180deg, transparent, {VIOLET}, transparent); }}

@keyframes beamPulse {{
    0%, 100% {{ opacity: 0.15; }}
    50% {{ opacity: 0.45; }}
}}

/* Kill every white Streamlit chrome layer */
[data-testid="stHeader"] {{
    background: transparent !important;
}}

[data-testid="stBottomBlockContainer"],
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stChatInput"],
[data-testid="stChatInputContainer"],
.stChatFloatingInputContainer,
footer {{
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
}}

[data-testid="stBottomBlockContainer"] {{
    background: linear-gradient(0deg, {BG} 70%, rgba(10,10,22,0)) !important;
    padding-bottom: 38px !important;
    position: relative;
}}

[data-testid="stBottomBlockContainer"]::after {{
    content: "⚡ Powered by Gemini AI  ·  Live Web Search  ·  ReAct Reasoning Loop";
    position: absolute;
    bottom: 8px;
    left: 50%;
    transform: translateX(-50%);
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.5px;
    color: {TEAL};
    opacity: 0.85;
    white-space: nowrap;
}}

[data-baseweb="textarea"] {{
    background-color: #0d0d1a !important;
    box-shadow: none !important;
}}

.block-container {{
    padding-top: 2rem !important;
    max-width: 1100px !important;
    position: relative;
    z-index: 1;
}}

/* ---------- MOVING GLOW LAYER (on top of the static wash) ---------- */
.bg-glow {{
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}}

.bg-glow::before, .bg-glow::after {{
    content: "";
    position: absolute;
    width: 500px; height: 500px;
    border-radius: 50%;
    filter: blur(100px);
    opacity: 0.35;
}}

.bg-glow::before {{
    background: {VIOLET};
    top: -120px; left: 10%;
    animation: drift1 16s ease-in-out infinite;
}}

.bg-glow::after {{
    background: {TEAL};
    bottom: -100px; right: 5%;
    animation: drift2 20s ease-in-out infinite;
}}

@keyframes drift1 {{
    0%, 100% {{ transform: translate(0, 0); }}
    50% {{ transform: translate(60px, 50px); }}
}}

@keyframes drift2 {{
    0%, 100% {{ transform: translate(0, 0); }}
    50% {{ transform: translate(-60px, -40px); }}
}}

.circuit-layer {{
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 0;
    opacity: 0.3;
    background-image: radial-gradient(circle, rgba(124,92,255,0.6) 1px, transparent 1px);
    background-size: 40px 40px;
    animation: pulseGrid 6s ease-in-out infinite;
}}

@keyframes pulseGrid {{
    0%, 100% {{ opacity: 0.18; }}
    50% {{ opacity: 0.38; }}
}}

/* slow-moving spotlight for extra depth/motion */
.spotlight {{
    position: fixed;
    top: -10%;
    left: -10%;
    width: 60%;
    height: 60%;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(124,92,255,0.25), transparent 70%);
    filter: blur(60px);
    z-index: 0;
    pointer-events: none;
    animation: spotlightMove 25s ease-in-out infinite;
}}

@keyframes spotlightMove {{
    0%, 100% {{ transform: translate(0, 0); }}
    33% {{ transform: translate(60%, 40%); }}
    66% {{ transform: translate(20%, 70%); }}
}}

/* ---------- HEADER: asymmetric, left title + right spec card ---------- */
.header-row {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 40px;
    padding: 20px 0 30px 0;
    position: relative;
    z-index: 1;
    flex-wrap: wrap;
}}

.header-left {{
    flex: 1;
    min-width: 320px;
}}

.header-left h1 {{
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.6em;
    letter-spacing: 0.5px;
    color: #ffffff;
    text-shadow: 0 0 18px rgba(0,229,199,0.6), 0 0 36px rgba(124,92,255,0.35);
    margin: 0 0 14px 0;
}}

.header-left p {{
    color: #c3c8e0;
    font-size: 15px;
    max-width: 580px;
    line-height: 1.8;
    border-left: 2px solid rgba(124,92,255,0.5);
    padding-left: 14px;
}}

.header-left .hl {{
    color: {TEAL};
    font-weight: 700;
    background: rgba(0,229,199,0.14);
    padding: 1px 7px;
    border-radius: 5px;
}}

.header-left .hl2 {{
    color: {VIOLET};
    font-weight: 700;
    background: rgba(124,92,255,0.16);
    padding: 1px 7px;
    border-radius: 5px;
}}

.spec-card {{
    min-width: 230px;
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(124,92,255,0.35);
    border-radius: 12px;
    padding: 16px 18px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #9aa3c4;
    box-shadow: 0 10px 40px rgba(0,0,0,0.45);
    transition: transform 0.3s ease;
}}

.spec-card:hover {{
    transform: translateY(-3px);
}}

.spec-card .spec-title {{
    color: {VIOLET};
    letter-spacing: 1.5px;
    font-size: 11px;
    margin-bottom: 10px;
    display: block;
}}

.spec-row {{
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    border-bottom: 1px dashed rgba(255,255,255,0.08);
}}

.spec-row span:last-child {{
    color: {TEAL};
}}

/* ---------- CHAT MESSAGE BASE ---------- */
[data-testid="stChatMessage"] {{
    position: relative;
    z-index: 1;
    background-color: rgba(255,255,255,0.04);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border-radius: 14px;
    padding: 10px 14px;
    margin-bottom: 4px;
    box-shadow: 0 8px 28px rgba(0,0,0,0.35);
    animation: fadeInUp 0.4s ease;
}}

@keyframes fadeInUp {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
    border-left: 3px solid {VIOLET};
    background-color: rgba(124,92,255,0.07);
}}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {{
    border-left: 3px solid {TEAL};
    background-color: rgba(0,229,199,0.05);
}}

p, span, label, li {{
    color: #d7dcee;
}}

/* ---------- SESSION DIVIDER CHIP ---------- */
.session-chip {{
    display: inline-block;
    margin: 26px 0 10px 0;
    padding: 4px 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 1px;
    color: {TEAL};
    border: 1px solid rgba(0,229,199,0.4);
    border-radius: 20px;
    background: rgba(0,229,199,0.06);
    position: relative;
    z-index: 1;
}}

/* ---------- REASONING / THOUGHT CONSOLE ---------- */
[class*="st-key-reasoning_box"] [data-testid="stExpander"] {{
    background-color: rgba(6,7,13,0.85) !important;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(0,229,199,0.3) !important;
    border-radius: 10px !important;
    box-shadow: 0 6px 24px rgba(0,0,0,0.35);
    font-family: 'JetBrains Mono', monospace !important;
}}

[class*="st-key-reasoning_box"] [data-testid="stExpander"] summary {{
    color: {TEAL} !important;
    font-size: 13px !important;
}}

[class*="st-key-reasoning_box"] p {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12.5px !important;
    color: #8fe8d8 !important;
    line-height: 1.6;
}}

/* ---------- ANSWER — THE FOCAL POINT ---------- */
[class*="st-key-answer_box"] {{
    background: linear-gradient(135deg, rgba(124,92,255,0.2), rgba(0,229,199,0.14));
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1.5px solid rgba(124,92,255,0.55);
    border-left: 5px solid {TEAL};
    border-radius: 14px;
    padding: 20px 22px !important;
    margin-top: 12px;
    transform: translateZ(0);
    animation: answerGlow 2.5s ease-in-out infinite;
}}

@keyframes answerGlow {{
    0%, 100% {{ box-shadow: 0 14px 40px rgba(0,0,0,0.4), 0 0 25px rgba(124,92,255,0.25); }}
    50% {{ box-shadow: 0 14px 40px rgba(0,0,0,0.4), 0 0 42px rgba(0,229,199,0.35); }}
}}

[class*="st-key-answer_box"] p {{
    font-size: 17px !important;
    color: #ffffff !important;
    line-height: 1.75 !important;
    font-weight: 500;
}}

.answer-label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11.5px;
    letter-spacing: 2px;
    color: {TEAL};
    margin-bottom: 10px;
    display: block;
}}

/* ---------- SOURCES — QUIET, REFERENCE STYLE ---------- */
[class*="st-key-sources_box"] [data-testid="stExpander"] {{
    background-color: transparent !important;
    border: none !important;
    border-top: 1px dashed rgba(255,255,255,0.12) !important;
    border-radius: 0 !important;
    margin-top: 10px;
    padding-top: 6px;
}}

[class*="st-key-sources_box"] [data-testid="stExpander"] summary {{
    color: #6b7390 !important;
    font-size: 12px !important;
}}

[class*="st-key-sources_box"] p, [class*="st-key-sources_box"] li {{
    font-size: 12px !important;
    color: #6b7390 !important;
}}

[class*="st-key-sources_box"] a {{
    color: #9aa3c4 !important;
}}

/* ---------- CHAT INPUT ---------- */
[data-testid="stChatInput"] {{
    background: transparent !important;
}}

/* remove every default browser/Streamlit focus outline, everywhere in the input */
[data-testid="stChatInput"] *:focus,
[data-testid="stChatInput"] *:focus-visible {{
    outline-color: #00E5C7 !important;
    outline-offset: 2px !important;
}}

[data-testid="stChatInput"] [data-baseweb="base-input"] {{
    background-color: #0d0d1a !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    transition: border 0.2s, box-shadow 0.2s;
}}

/* our own glow appears only on the real container, only on focus — nowhere else */
[data-testid="stChatInput"] [data-baseweb="base-input"]:focus-within {{
    border: 1.5px solid {TEAL} !important;
    box-shadow: 0 0 16px rgba(0,229,199,0.45) !important;
}}

[data-testid="stChatInput"] textarea {{
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #f3f4fb !important;
}}

[data-testid="stChatInput"] textarea::placeholder {{
    color: #8891b5 !important;
    opacity: 1 !important;
}}

/* send button — visible identity even before hover */
[data-testid="stChatInputSubmitButton"] {{
    background: linear-gradient(135deg, {VIOLET}, {TEAL}) !important;
    border-radius: 9px !important;
    border: none !important;
    opacity: 1 !important;
}}

[data-testid="stChatInputSubmitButton"] svg {{
    fill: #0a0a16 !important;
    color: #0a0a16 !important;
}}

[data-testid="stChatInputSubmitButton"]:hover {{
    box-shadow: 0 0 14px rgba(0,229,199,0.55) !important;
    transform: scale(1.04);
}}

/* ---------- SPINNER ---------- */
[data-testid="stSpinner"] p {{
    color: {TEAL} !important;
    font-family: 'JetBrains Mono', monospace !important;
}}
</style>

<div class="mesh-layer"></div>
<div class="spotlight"></div>
<div class="bg-glow"></div>
<div class="circuit-layer"></div>
<div class="side-beam left"></div>
<div class="side-beam right"></div>
<div class="vignette"></div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# AGENT LOGIC
# ---------------------------------------------------------------------------
def search_web(query, max_results=3):
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append({"title": r["title"], "snippet": r["body"], "link": r["href"]})
    return results

SYSTEM_PROMPT = """You are a research agent that answers questions by searching the web.

You work in a loop of Thought, Action, Observation.

At each step, respond in EXACTLY this format (nothing else):

Thought: <your reasoning about what to do next>
Action: <either "search: <search query>" or "finish: <your final answer>">

Rules:
- Use "search: <query>" when you need more information.
- Use "finish: <answer>" only when you have enough information to answer confidently.
- Keep search queries short and specific.
- Do not make up information. Only answer using what you learned from search results.
- Give the final answer in 2-4 clear sentences.
"""

def run_agent(question, max_steps=4):
    history = f"Question: {question}\n"
    sources = []
    steps = []

    for step in range(max_steps):
        prompt = SYSTEM_PROMPT + "\n" + history + "\nWhat is your next Thought and Action?"
        response = model.generate_content(prompt)
        text = response.text.strip()
        history += text + "\n"

        thought = ""
        if "Thought:" in text:
            thought = text.split("Thought:")[1].split("Action:")[0].strip()

        if "Action: finish:" in text:
            final_answer = text.split("Action: finish:")[1].strip()
            steps.append({"thought": thought, "query": None})
            return final_answer, sources, steps

        if "Action: search:" in text:
            query = text.split("Action: search:")[1].strip()
            results = search_web(query)
            for r in results:
                sources.append({"title": r["title"], "link": r["link"]})
            observation = "\n".join([f"- {r['title']}: {r['snippet'][:200]}" for r in results])
            history += f"Observation: {observation}\n"
            steps.append({"thought": thought, "query": query})

    return "I couldn't find a confident answer within the allowed steps. Try rephrasing your question.", sources, steps

def render_steps(steps):
    for i, s in enumerate(steps, start=1):
        st.markdown(f"`STEP {i}` {s['thought']}")
        if s["query"]:
            st.markdown(f"🔎 `search:` *{s['query']}*")

USER_AVATAR = "🧑‍🔬"
AGENT_AVATAR = "🧠"

def render_turn(idx, question, answer, sources, steps):
    st.markdown(f'<div class="session-chip">QUERY #{idx + 1}</div>', unsafe_allow_html=True)

    with st.chat_message("user", avatar=USER_AVATAR):
        st.write(question)

    with st.chat_message("assistant", avatar=AGENT_AVATAR):
        with st.container(key=f"reasoning_box_{idx}"):
            with st.expander("AGENT REASONING", expanded=False):
                render_steps(steps)

        with st.container(key=f"answer_box_{idx}"):
            st.markdown('<span class="answer-label">ANSWER</span>', unsafe_allow_html=True)
            st.write(answer)

        if sources:
            with st.container(key=f"sources_box_{idx}"):
                with st.expander("Sources"):
                    for s in sources:
                        st.markdown(f"- [{s['title']}]({s['link']})")

# ---------------------------------------------------------------------------
# HEADER — asymmetric: title+description left, spec card right
# ---------------------------------------------------------------------------
st.markdown("""
<div class="header-row">
  <div class="header-left">
    <h1>ReAct Agent</h1>
    <p>An autonomous AI agent that <span class="hl">thinks before it acts</span>. Ask a question, and watch it
    reason step by step — deciding what to search for, reading <span class="hl2">live results from the web</span>,
    and refining its approach until it's confident. Unlike a standard chatbot, this agent plans, investigates,
    and verifies, with every answer <span class="hl">fully grounded in real, current sources</span> — and the
    entire thought process visible to you.</p>
  </div>
  <div class="spec-card">
    <span class="spec-title">AGENT SPEC</span>
    <div class="spec-row"><span>Model</span><span>Gemini 3.5 Flash</span></div>
    <div class="spec-row"><span>Tool</span><span>Live Web Search</span></div>
    <div class="spec-row"><span>Pattern</span><span>ReAct Loop</span></div>
    <div class="spec-row"><span>Max Steps</span><span>4</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# CHAT STATE + RENDER
# ---------------------------------------------------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for idx, entry in enumerate(st.session_state.chat_history):
    render_turn(idx, entry["question"], entry["answer"], entry["sources"], entry["steps"])

question = st.chat_input("Ask something that needs current information...")

if question:
    idx = len(st.session_state.chat_history)
    st.markdown(f'<div class="session-chip">QUERY #{idx + 1}</div>', unsafe_allow_html=True)

    with st.chat_message("user", avatar=USER_AVATAR):
        st.write(question)

    with st.chat_message("assistant", avatar=AGENT_AVATAR):
        with st.spinner("Thinking..."):
            answer, sources, steps = run_agent(question)

        with st.container(key=f"reasoning_box_{idx}"):
            with st.expander("AGENT REASONING", expanded=True):
                render_steps(steps)

        with st.container(key=f"answer_box_{idx}"):
            st.markdown('<span class="answer-label">ANSWER</span>', unsafe_allow_html=True)
            st.write(answer)

        if sources:
            with st.container(key=f"sources_box_{idx}"):
                with st.expander("Sources"):
                    for s in sources:
                        st.markdown(f"- [{s['title']}]({s['link']})")

    st.session_state.chat_history.append({
        "question": question,
        "answer": answer,
        "sources": sources,
        "steps": steps
    })

