import streamlit as st
import time
from pipeline import get_or_gather_data, run_critic
from agents import writer_chain # Needed for streaming!

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)



# --- Session State Initialization ---
if "phase" not in st.session_state:
    st.session_state.phase = "input"
if "topic_val" not in st.session_state:
    st.session_state.topic_val = ""
if "raw_data" not in st.session_state:
    st.session_state.raw_data = {}
if "scraped_context" not in st.session_state:
    st.session_state.scraped_context = ""
if "final_report" not in st.session_state:
    st.session_state.final_report = ""
if "critic_feedback" not in st.session_state:
    st.session_state.critic_feedback = ""

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #e8e4dc;
}

/* ── Animated Background ── */
@keyframes backgroundShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.stApp {
    background: linear-gradient(-45deg, #0a0a0f, #141018, #1a0f0a, #0a0a0f);
    background-size: 400% 400%;
    animation: backgroundShift 15s ease infinite;
}

/* ── Animations ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulseGlow {
    0% { box-shadow: 0 0 0 0 rgba(255, 140, 50, 0.4); }
    70% { box-shadow: 0 0 0 6px rgba(255, 140, 50, 0); }
    100% { box-shadow: 0 0 0 0 rgba(255, 140, 50, 0); }
}

@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1200px; }

/* ── Hero header ── */
.hero {
    text-align: center;
    padding: 3.5rem 0 2.5rem;
    position: relative;
    animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #ff8c32;
    margin-bottom: 1rem;
    opacity: 0.9;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.8rem, 6vw, 5rem);
    font-weight: 800;
    line-height: 1.0;
    letter-spacing: -0.03em;
    color: #f0ebe0;
    margin: 0 0 1rem;
    text-shadow: 0 4px 20px rgba(255, 140, 50, 0.15);
}
.hero h1 span {
    background: linear-gradient(135deg, #ff8c32 0%, #ff5a1a 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: 1.05rem;
    font-weight: 300;
    color: #a09890;
    max-width: 540px;
    margin: 0 auto;
    line-height: 1.65;
}

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,140,50,0.3), transparent);
    margin: 2rem 0;
    opacity: 0;
    animation: fadeUp 0.8s 0.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* ── Input card (Glassmorphism) ── */
.input-card {
    background: rgba(20, 20, 25, 0.4);
    border: 1px solid rgba(255,140,50,0.2);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    opacity: 0;
    animation: fadeUp 0.8s 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* ── Streamlit input overrides ── */
.stTextInput > div > div > input {
    background: rgba(0,0,0,0.2) !important;
    border: 1px solid rgba(255,140,50,0.3) !important;
    border-radius: 10px !important;
    color: #f0ebe0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
    transition: all 0.3s ease !important;
}
.stTextInput > div > div > input:focus {
    border-color: #ff8c32 !important;
    box-shadow: 0 0 15px rgba(255,140,50,0.2) !important;
    background: rgba(0,0,0,0.4) !important;
}
.stTextInput > label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: #ff8c32 !important;
    font-weight: 500 !important;
}

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, #ff8c32 0%, #ff5a1a 100%) !important;
    color: #0a0a0f !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.05em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.7rem 2.2rem !important;
    cursor: pointer !important;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    box-shadow: 0 4px 15px rgba(255,140,50,0.2) !important;
    width: 100%;
}
.stButton > button:hover {
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 10px 25px rgba(255,140,50,0.4) !important;
}
.stButton > button:active {
    transform: translateY(0) scale(0.98) !important;
}

/* ── Pipeline step cards ── */
.step-card {
    background: rgba(20, 20, 25, 0.4);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(8px);
    transition: all 0.4s ease;
    opacity: 0;
    animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* Staggered load for step cards */
.step-card:nth-child(2) { animation-delay: 0.4s; }
.step-card:nth-child(3) { animation-delay: 0.5s; }
.step-card:nth-child(4) { animation-delay: 0.6s; }
.step-card:nth-child(5) { animation-delay: 0.7s; }

.step-card:hover {
    transform: translateX(4px);
    background: rgba(30, 30, 35, 0.5);
}

.step-card.active {
    border-color: rgba(255,140,50,0.6);
    background: rgba(255,140,50,0.05);
    box-shadow: 0 0 20px rgba(255,140,50,0.1);
    animation: fadeUp 0.8s forwards, pulseGlow 2s infinite !important;
}
.step-card.done {
    border-color: rgba(80,200,120,0.4);
    background: rgba(80,200,120,0.03);
}
.step-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 4px;
    border-radius: 14px 0 0 14px;
    background: rgba(255,255,255,0.05);
    transition: background 0.4s ease;
}
.step-card.active::before { 
    background: #ff8c32; 
    box-shadow: 0 0 10px #ff8c32;
}
.step-card.done::before   { background: #50c878; }

.step-header {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.3rem;
}
.step-num {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    color: #ff8c32;
    background: rgba(255,140,50,0.1);
    padding: 2px 6px;
    border-radius: 4px;
}
.step-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #f0ebe0;
}
.step-status {
    margin-left: auto;
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    font-weight: 600;
}
.status-waiting  { color: #666; }
.status-running  { color: #ff8c32; animation: blink 1.5s infinite; }
.status-done     { color: #50c878; }

/* ── Result panels ── */
.result-panel, .report-panel, .feedback-panel {
    background: rgba(20, 20, 25, 0.4);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-top: 1rem;
    margin-bottom: 1.5rem;
    opacity: 0;
    animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.result-panel { border: 1px solid rgba(255,255,255,0.1); }
.report-panel { border: 1px solid rgba(255,140,50,0.3); box-shadow: 0 8px 30px rgba(255,140,50,0.05); }
.feedback-panel { border: 1px solid rgba(80,200,120,0.3); box-shadow: 0 8px 30px rgba(80,200,120,0.05); }

.result-panel-title {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #ff8c32;
    margin-bottom: 1rem;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid rgba(255,140,50,0.15);
}
.result-content {
    font-size: 0.95rem;
    line-height: 1.8;
    color: #d8d3ca;
    white-space: pre-wrap;
    font-family: 'DM Sans', sans-serif;
}

.panel-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    padding-bottom: 0.7rem;
    font-weight: 600;
}
.panel-label.orange {
    color: #ff8c32;
    border-bottom: 1px solid rgba(255,140,50,0.2);
}
.panel-label.green {
    color: #50c878;
    border-bottom: 1px solid rgba(80,200,120,0.2);
}

/* ── Progress text ── */
.stSpinner > div { color: #ff8c32 !important; }

/* ── Expander ── */
details summary {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
    color: #a09890 !important;
    letter-spacing: 0.1em !important;
    cursor: pointer;
    transition: color 0.3s ease;
}
details summary:hover { color: #ff8c32 !important; }

/* ── Section heading ── */
.section-heading {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: #f0ebe0;
    margin: 2rem 0 1rem;
    opacity: 0;
    animation: fadeUp 0.8s 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* ── Example Chips ── */
.example-chip {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 0.35rem 0.8rem;
    font-size: 0.75rem;
    color: #b0a8a0;
    font-family: 'DM Sans', sans-serif;
    cursor: pointer;
    transition: all 0.3s ease;
}
.example-chip:hover {
    background: rgba(255,140,50,0.1);
    border-color: rgba(255,140,50,0.4);
    color: #ff8c32;
    transform: translateY(-2px);
}

/* ── Toast-style notice ── */
.notice {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    color: #605850;
    text-align: center;
    margin-top: 4rem;
    letter-spacing: 0.08em;
    opacity: 0;
    animation: fadeUp 1s 1s forwards;
}
</style>
""", unsafe_allow_html=True)


# ── Helper: render a step card ────────────────────────────────────────────────
def step_card(num: str, title: str, state: str, desc: str = ""):
    status_map = {
        "waiting": ("WAITING", "status-waiting"),
        "running": ("● RUNNING", "status-running"),
        "done":    ("✓ DONE",   "status-done"),
    }
    label, cls = status_map.get(state, ("", ""))
    card_cls = {"running": "active", "done": "done"}.get(state, "")
    st.markdown(f"""
    <div class="step-card {card_cls}">
        <div class="step-header">
            <span class="step-num">{num}</span>
            <span class="step-title">{title}</span>
            <span class="step-status {cls}">{label}</span>
        </div>
        {"<div style='font-size:0.85rem;color:#807870;margin-top:0.4rem;line-height:1.4;'>"+desc+"</div>" if desc else ""}
    </div>
    """, unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Multi-Agent AI System</div>
    <h1>Research<span>Mind</span></h1>
    <p class="hero-sub">
        Four specialized AI agents collaborate — searching, scraping, writing,
        and critiquing — to deliver a polished research report on any topic.
    </p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ── Layout: input left, pipeline right ───────────────────────────────────────
col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        key="topic_input",
        label_visibility="visible",
    )
    run_btn = st.button("⚡  Run Research Pipeline", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Example chips
    st.markdown("""
    <div style="display:flex;gap:0.6rem;flex-wrap:wrap;margin-bottom:1.5rem;align-items:center; opacity:0; animation: fadeUp 0.8s 0.4s forwards;">
        <span style="font-family:'DM Mono',monospace;font-size:0.68rem;color:#605850;letter-spacing:0.1em;margin-right:4px;">TRY →</span>
    """, unsafe_allow_html=True)
    examples = ["LLM agents 2025", "CRISPR gene editing", "Fusion energy progress"]
    for ex in examples:
        st.markdown(f'<span class="example-chip">{ex}</span>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_pipeline:
    st.markdown('<div class="section-heading">Pipeline</div>', unsafe_allow_html=True)

    r = st.session_state.results
    done = st.session_state.done

    def s(step):
        if not r:
            return "waiting"
        steps = ["search", "reader", "writer", "critic"]
        idx = steps.index(step)
        completed = list(r.keys())
        # figure out which steps are done
        if step in r:
            return "done"
        # which step is running now (first not in r)
        if st.session_state.running:
            for i, k in enumerate(steps):
                if k not in r:
                    return "running" if k == step else "waiting"
        return "waiting"

    step_card("01", "Search Agent",  s("search"), "Gathers recent web information")
    step_card("02", "Reader Agent",  s("reader"), "Scrapes & extracts deep content")
    step_card("03", "Writer Chain",  s("writer"), "Drafts the full research report")
    step_card("04", "Critic Chain",  s("critic"), "Reviews & scores the report")


# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.topic_val = topic
        st.session_state.phase = "gathering"
        st.session_state.final_report = ""
        st.session_state.critic_feedback = ""
        st.rerun()

# ==========================================
# PHASE 1: Gather Data (Search & Scrape)
# ==========================================
if st.session_state.phase == "gathering":
    with st.spinner("🔍 Agents are searching the web (or checking memory)..."):
        
        # USE THE NEW MEMORY FUNCTION HERE
        st.session_state.raw_data = get_or_gather_data(st.session_state.topic_val)
        
        # Combine search and scrape for the human to review
        combined_context = (
            f"SEARCH RESULTS:\n{st.session_state.raw_data.get('search_results', '')}\n\n"
            f"SCRAPED CONTENT:\n{st.session_state.raw_data.get('scraped_content', '')}"
        )
        st.session_state.scraped_context = combined_context
        st.session_state.phase = "review"
        st.rerun()

# ==========================================
# PHASE 2: Human-in-the-Loop Review
# ==========================================
if st.session_state.phase == "review":
    st.markdown('<div class="section-heading">🛑 Review Scraped Context</div>', unsafe_allow_html=True)
    st.info("The agents have gathered the following context. You can edit this text to guide the Writer agent, delete irrelevant info, or just approve it as-is.")
    
    # Editable text area
    edited_context = st.text_area(
        "Edit Context Before Writing", 
        value=st.session_state.scraped_context, 
        height=400
    )
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("✅ Approve & Generate Report", use_container_width=True):
            st.session_state.scraped_context = edited_context
            st.session_state.phase = "writing"
            st.rerun()
    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.phase = "input"
            st.rerun()

# ==========================================
# PHASE 3: Stream Writing & Critic
# ==========================================
if st.session_state.phase == "writing":
    st.markdown('<div class="section-heading">📝 Drafting Report...</div>', unsafe_allow_html=True)
    
    report_container = st.empty()
    full_text = ""
    
    # 1. Stream the writer output
    stream = writer_chain.stream({
        "topic": st.session_state.topic_val,
        "research": st.session_state.scraped_context
    })
    
    for chunk in stream:
        # Extract text based on LangChain object type
        if hasattr(chunk, "content"):
            text_chunk = chunk.content
        elif isinstance(chunk, dict) and "text" in chunk:
            text_chunk = chunk["text"]
        else:
            text_chunk = str(chunk)
            
        full_text += text_chunk
        # Add a cursor block while typing
        report_container.markdown(f'<div class="result-panel">{full_text} ▌</div>', unsafe_allow_html=True)
        
    # Remove cursor when done
    report_container.markdown(f'<div class="report-panel">{full_text}</div>', unsafe_allow_html=True)
    st.session_state.final_report = full_text
    
    # 2. Run the Critic
    with st.spinner("🧐 Critic Agent is reviewing the final draft..."):
        st.session_state.critic_feedback = run_critic(st.session_state.final_report)
    
    st.session_state.phase = "done"
    st.rerun()

# ==========================================
# PHASE 4: Display Final Results
# ==========================================
if st.session_state.phase == "done":
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Final Results</div>', unsafe_allow_html=True)

    # Final Report
    st.markdown("""
    <div class="report-panel">
        <div class="panel-label orange">📝 Final Research Report</div>
    """, unsafe_allow_html=True)
    st.markdown(st.session_state.final_report)
    st.markdown("</div>", unsafe_allow_html=True)

    # Download button
    st.download_button(
        label="⬇ Download Report (.md)",
        data=st.session_state.final_report,
        file_name=f"research_report_{int(time.time())}.md",
        mime="text/markdown",
    )

    # Critic Feedback
    st.markdown("""
    <div class="feedback-panel">
        <div class="panel-label green">🧐 Critic Feedback</div>
    """, unsafe_allow_html=True)
    st.markdown(st.session_state.critic_feedback)
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("Start New Research"):
        st.session_state.phase = "input"
        st.rerun()


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    ResearchMind · Powered by LangChain multi-agent pipeline · Built with Streamlit
</div>
""", unsafe_allow_html=True)