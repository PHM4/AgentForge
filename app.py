# app.py
# streamlit ui for agentforge
# run: streamlit run app.py

import streamlit as st
import json
import time
from agent.core import AgentForge

st.set_page_config(
    page_title="AgentForge",
    page_icon="AF",
    layout="centered",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;500;600&display=swap');

    .stApp {
        background-color: #0a0a0a;
        color: #d4d4d4;
    }
    .main .block-container {
        max-width: 860px;
        padding-top: 2.5rem;
    }

    /* header */
    .af-head {
        padding-bottom: 1rem;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid #1a1a1a;
    }
    .af-head h1 {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.6rem;
        font-weight: 600;
        color: #fff;
        margin: 0 0 0.2rem 0;
    }
    .af-head p {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #555;
        margin: 0;
    }

    /* info bar */
    .info-bar {
        background: #0a0a0a;
        border: 1px solid #1e1e1e;
        border-radius: 4px;
        padding: 0.8rem 1rem;
        margin-bottom: 1.5rem;
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem;
        color: #666;
        line-height: 1.6;
    }
    .info-bar strong { color: #999; }

    /* step cards */
    .s-card {
        background: #0a0a0a;
        border: 1px solid #1e1e1e;
        border-radius: 4px;
        padding: 0.8rem 1rem;
        margin: 0.4rem 0;
        font-family: 'Inter', sans-serif;
        font-size: 0.84rem;
        line-height: 1.5;
    }
    .s-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: #444;
        letter-spacing: 0.04em;
        margin-bottom: 0.3rem;
    }
    .s-thought { color: #b0b0b0; }
    .s-tool {
        color: #7aa2f7;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
    }

    /* metrics */
    .m-bar {
        display: flex;
        gap: 1.5rem;
        padding: 0.7rem 0;
        margin-top: 0.5rem;
        border-top: 1px solid #1a1a1a;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: #444;
    }
    .m-val { color: #7aa2f7; }

    /* inputs */
    .stTextArea textarea {
        background-color: #0a0a0a !important;
        border: 1px solid #1e1e1e !important;
        color: #d4d4d4 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.88rem !important;
        border-radius: 4px !important;
    }
    .stTextArea textarea:focus {
        border-color: #7aa2f7 !important;
        box-shadow: none !important;
    }

    /* buttons */
    .stButton > button {
        background-color: #0a0a0a !important;
        border: 1px solid #1e1e1e !important;
        color: #d4d4d4 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.84rem !important;
        border-radius: 4px !important;
    }
    .stButton > button:hover {
        border-color: #7aa2f7 !important;
        color: #fff !important;
    }
    .stButton > button[kind="primary"] {
        background-color: #7aa2f7 !important;
        color: #0a0a0a !important;
        border: none !important;
        font-weight: 600 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #6090e0 !important;
    }

    /* select */
    .stSelectbox > div > div {
        background-color: #0a0a0a !important;
        border-color: #1e1e1e !important;
        color: #d4d4d4 !important;
    }
    .stSelectbox label { color: #888 !important; font-size: 0.84rem !important; }

    /* expander */
    .streamlit-expanderHeader {
        background-color: #0a0a0a !important;
        color: #666 !important;
        font-size: 0.8rem !important;
    }

    /* footer */
    .af-footer {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #333;
        text-align: center;
        padding-top: 3rem;
    }
    .af-footer a { color: #555; text-decoration: none; }
    .af-footer a:hover { color: #7aa2f7; }

    /* hide streamlit stuff */
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# -- header --
st.markdown("""
<div class="af-head">
    <h1>AgentForge</h1>
    <p>research and code analysis agent — react pattern, tool use</p>
</div>
""", unsafe_allow_html=True)

# -- how it works + mode selector on the same row --
st.markdown(
    '<div class="info-bar">'
    '<strong>how it works:</strong> '
    'think → pick a tool → use it → read the result → repeat until done. '
    'tools available: web search, file read/write, python execution.'
    '</div>',
    unsafe_allow_html=True,
)

# mode selector inline
mode = st.selectbox(
    "mode",
    options=["general", "research", "code_review"],
    format_func=lambda x: x.replace("_", " "),
)

# -- examples --
st.markdown("**try an example or type your own**")
c1, c2, c3 = st.columns(3)

with c1:
    if st.button("research a topic", use_container_width=True):
        st.session_state.task_input = (
            "Research the current state of AI agents in 2025. "
            "What frameworks are popular, what are the key trends, "
            "and what challenges remain?"
        )
with c2:
    if st.button("review some code", use_container_width=True):
        st.session_state.task_input = (
            "Write a Python function that implements binary search, "
            "then review it for bugs, edge cases, and performance. "
            "Save the reviewed code to a file."
        )
with c3:
    if st.button("solve a problem", use_container_width=True):
        st.session_state.task_input = (
            "What are the top 5 most energy-efficient programming languages? "
            "Search for benchmarks and write a short comparison."
        )

task = st.text_area(
    "task input",
    value=st.session_state.get("task_input", ""),
    height=100,
    placeholder="what do you want the agent to do...",
    label_visibility="collapsed",
)


# -- run --
if st.button("run", type="primary", use_container_width=True):
    if not task.strip():
        st.warning("type something first")
    else:
        agent = AgentForge(mode=mode)
        status = st.status("working...", expanded=True)
        sc = status.container()

        with st.spinner(""):
            t0 = time.time()
            result = agent.run(task, verbose=False)
            dt = time.time() - t0

        status.update(
            label=f"done — {result['total_steps']} steps, {result['tool_calls']} tools, {dt:.1f}s",
            state="complete",
            expanded=True,
        )

        for step in result["steps"]:
            with sc:
                for a in step["actions"]:
                    if a["type"] == "thought":
                        txt = a["content"][:400]
                        if len(a["content"]) > 400:
                            txt += "..."
                        st.markdown(
                            f'<div class="s-card">'
                            f'<div class="s-label">step {step["step"]} — thought</div>'
                            f'<div class="s-thought">{txt}</div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                    elif a["type"] == "tool_use":
                        st.markdown(
                            f'<div class="s-card">'
                            f'<div class="s-label">step {step["step"]} — tool</div>'
                            f'<div class="s-tool">{a["tool"]}</div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                        with st.expander(f"{a['tool']} details"):
                            st.json(a["input"])
                            st.code(a["result"][:800], language="text")

        st.markdown("---")
        st.markdown(result["result"])

        st.markdown(
            f'<div class="m-bar">'
            f'<span>steps <span class="m-val">{result["total_steps"]}</span></span>'
            f'<span>tool calls <span class="m-val">{result["tool_calls"]}</span></span>'
            f'<span>time <span class="m-val">{dt:.1f}s</span></span>'
            f'</div>',
            unsafe_allow_html=True,
        )

# footer
st.markdown(
    '<div class="af-footer">built by <a href="https://phm4.co.uk">PHM4</a></div>',
    unsafe_allow_html=True,
)
