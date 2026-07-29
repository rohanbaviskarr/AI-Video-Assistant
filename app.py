import streamlit as st
import time
from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Video Assistant",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS — "Studio Deck" theme ────────────────────────────────────────
# Concept: an analog tape-deck / mixing-console front panel. VU-meter style
# progress, cassette-label cards, timecoded chat transcript, a pulsing REC dot.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg: #0b0c0d;
    --panel: #17191b;
    --panel-2: #1f2224;
    --border: #34383b;
    --amber: #e8a33d;
    --amber-glow: #ffc369;
    --rec: #e0483f;
    --signal: #57cbb8;
    --text: #f2ede3;
    --text-muted: #93938d;
}

html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Space Grotesk', sans-serif;
}
.stApp { background: var(--bg) !important; }

/* faint brushed-metal texture */
.stApp::before {
    content: '';
    position: fixed; inset: 0;
    background-image: repeating-linear-gradient(
        180deg, rgba(255,255,255,0.012) 0px, rgba(255,255,255,0.012) 1px,
        transparent 1px, transparent 3px
    );
    pointer-events: none; z-index: 0;
}

[data-testid="stSidebar"] {
    background: var(--panel) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

h1, h2, h3, h4 { font-family: 'Oswald', sans-serif !important; letter-spacing: 0.02em; }

/* ── Header / face plate ── */
.deck-header {
    display: flex; align-items: baseline; gap: 0.9rem;
    padding-bottom: 0.6rem;
    border-bottom: 2px solid var(--border);
    margin-bottom: 1.6rem;
    position: relative;
}
.deck-header::after {
    content: '';
    position: absolute; bottom: -2px; left: 0; width: 140px; height: 2px;
    background: linear-gradient(90deg, var(--amber), transparent);
}
.rec-dot {
    width: 11px; height: 11px; border-radius: 50%;
    background: var(--rec);
    box-shadow: 0 0 10px var(--rec);
    animation: rec-pulse 1.6s ease-in-out infinite;
    flex-shrink: 0;
}
@keyframes rec-pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.35; } }
.deck-title {
    font-family: 'Oswald', sans-serif;
    font-weight: 700;
    font-size: 2rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text);
}
.deck-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-muted);
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

/* ── Sidebar labels as panel groups ── */
.panel-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--amber);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.3rem;
    margin: 1rem 0 0.6rem 0;
}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stTextArea textarea {
    background: var(--panel-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 2px rgba(232,163,61,0.25) !important;
}
label, .stRadio label p { color: var(--text-muted) !important; font-size: 0.78rem !important; }

/* ── Buttons — chunky console button ── */
.stButton > button {
    background: linear-gradient(180deg, var(--amber-glow), var(--amber)) !important;
    color: #1a1206 !important;
    border: none !important;
    border-radius: 7px !important;
    font-family: 'Oswald', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    padding: 0.55rem 1.4rem !important;
    box-shadow: 0 3px 0 #8a5f1f, 0 6px 14px rgba(0,0,0,0.4) !important;
    transition: transform 0.08s ease !important;
}
.stButton > button:hover { transform: translateY(1px) !important; }
.stButton > button:active {
    transform: translateY(3px) !important;
    box-shadow: 0 0px 0 #8a5f1f, 0 2px 6px rgba(0,0,0,0.4) !important;
}
.stButton > button[kind="secondary"] {
    background: var(--panel-2) !important;
    color: var(--text) !important;
    box-shadow: 0 3px 0 #000, 0 6px 14px rgba(0,0,0,0.3) !important;
}

/* ── VU-meter step indicator ── */
.vu-row {
    display: flex; align-items: center; gap: 0.6rem;
    padding: 0.4rem 0.2rem;
}
.vu-icon { font-size: 0.9rem; width: 1.3rem; text-align: center; }
.vu-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem; color: var(--text-muted);
    flex-shrink: 0; width: 108px;
}
.vu-segments { display: flex; gap: 2px; flex: 1; }
.vu-seg { height: 8px; flex: 1; border-radius: 1px; background: var(--panel-2); border: 1px solid var(--border); }
.vu-seg.on-done  { background: var(--signal); border-color: var(--signal); }
.vu-seg.on-active{ background: var(--amber); border-color: var(--amber); animation: vu-flicker 0.5s infinite alternate; }
@keyframes vu-flicker { from { opacity: 1; } to { opacity: 0.45; } }

/* ── Cassette-label cards ── */
.tape-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1.3rem 1.4rem 1.1rem 1.4rem;
    margin-bottom: 1rem;
    position: relative;
}
.tape-card::before {
    content: '';
    position: absolute; top: 0; left: 14px; right: 14px; height: 1px;
    background-image: repeating-linear-gradient(90deg, var(--border) 0 6px, transparent 6px 12px);
}
.tape-eyebrow {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem; letter-spacing: 0.16em; text-transform: uppercase;
    color: var(--amber);
    display: flex; align-items: center; gap: 0.4rem;
    margin-bottom: 0.7rem;
}
.tape-body { font-size: 0.9rem; line-height: 1.7; color: var(--text); }

.title-strip {
    background: linear-gradient(135deg, var(--panel-2), var(--panel));
    border: 1px solid var(--border);
    border-left: 4px solid var(--amber);
    border-radius: 4px;
    padding: 1rem 1.3rem;
    margin-bottom: 1.2rem;
}
.title-strip .tape-eyebrow { color: var(--text-muted); }
.title-strip .title-text {
    font-family: 'Oswald', sans-serif; font-weight: 600; font-size: 1.5rem; color: var(--text);
}

/* ── Transcript reel box ── */
.reel-box {
    background: var(--panel-2);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1.1rem;
    max-height: 320px; overflow-y: auto;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem; line-height: 1.8;
    color: var(--text-muted);
    white-space: pre-wrap; word-break: break-word;
}

/* ── Timecoded chat transcript ── */
.chat-reel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1.1rem 1.2rem;
    max-height: 420px; overflow-y: auto;
    margin-bottom: 1rem;
}
.chat-line { margin-bottom: 0.9rem; }
.chat-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.66rem; letter-spacing: 0.1em; text-transform: uppercase;
    margin-right: 0.5rem;
}
.tag-you  { color: var(--amber); }
.tag-ai   { color: var(--signal); }
.chat-text { font-size: 0.87rem; line-height: 1.6; color: var(--text); }

.empty-console {
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    padding: 4.5rem 2rem; text-align: center;
    border: 1px dashed var(--border);
    border-radius: 6px;
}
.empty-console .reel-icon {
    width: 46px; height: 46px; border-radius: 50%;
    border: 3px solid var(--amber);
    position: relative;
    animation: spin 5s linear infinite;
    margin-bottom: 1.1rem;
}
.empty-console .reel-icon::before, .empty-console .reel-icon::after {
    content: ''; position: absolute; background: var(--amber); border-radius: 50%;
}
.empty-console .reel-icon::before { width: 6px; height: 6px; top: 6px; left: 6px; }
.empty-console .reel-icon::after { width: 6px; height: 6px; bottom: 6px; right: 6px; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.4rem 0 !important; }
.stProgress > div > div > div { background: var(--amber) !important; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--amber); }
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────────────────
for key, default in {
    "result": None,
    "chat_history": [],
    "pipeline_done": False,
    "pipeline_steps": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

PIPELINE_STEPS = [
    ("audio", "🔊", "Audio In"),
    ("transcript", "📝", "Transcript"),
    ("title", "🏷️", "Title"),
    ("summary", "📋", "Summary"),
    ("extract", "🔍", "Extraction"),
    ("rag", "🧠", "RAG Engine"),
]


def render_vu_step(key: str, icon: str, label: str):
    state = st.session_state.pipeline_steps.get(key, "pending")
    seg_class = "on-done" if state == "done" else ("on-active" if state == "active" else "")
    segs = "".join(f'<div class="vu-seg {seg_class}"></div>' for _ in range(10))
    st.markdown(f"""
    <div class="vu-row">
        <span class="vu-icon">{icon}</span>
        <span class="vu-label">{label}</span>
        <div class="vu-segments">{segs}</div>
    </div>""", unsafe_allow_html=True)


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="deck-title" style="font-size:1.3rem">🎛️ Studio Deck</div>', unsafe_allow_html=True)
    st.markdown('<div class="deck-sub">AI Video Assistant</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-label">Source</div>', unsafe_allow_html=True)
    source = st.text_input(
        "YouTube URL or File Path",
        placeholder="https://youtube.com/watch?v=... or /path/to/file.mp4",
        label_visibility="collapsed",
    )

    st.markdown('<div class="panel-label">Language</div>', unsafe_allow_html=True)
    language = st.selectbox("Language", ["english", "hinglish"], index=0, label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("● Analyse", use_container_width=True)

    if st.session_state.pipeline_done:
        st.markdown('<div class="panel-label">Signal Path</div>', unsafe_allow_html=True)
        for key, icon, label in PIPELINE_STEPS:
            render_vu_step(key, icon, label)

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="deck-header">
    <span class="rec-dot"></span>
    <div>
        <div class="deck-title">AI Video Assistant</div>
        <div class="deck-sub">Transcribe · Summarise · Chat with your recording</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Run Pipeline ─────────────────────────────────────────────────────────────
if run_btn:
    if not source.strip():
        st.error("Enter a YouTube URL or file path first.")
    else:
        st.session_state.pipeline_done = False
        st.session_state.result = None
        st.session_state.chat_history = []
        st.session_state.pipeline_steps = {}

        status_box = st.empty()

        def set_step(k, s):
            st.session_state.pipeline_steps[k] = s

        try:
            status_box.info("⚙️ Running pipeline — watch the signal path in the sidebar.")

            set_step("audio", "active")
            chunks = process_input(source)
            set_step("audio", "done")

            set_step("transcript", "active")
            transcript = transcribe_all(chunks, language)
            set_step("transcript", "done")

            set_step("title", "active")
            title = generate_title(transcript)
            set_step("title", "done")

            set_step("summary", "active")
            summary = summarize(transcript)
            set_step("summary", "done")

            set_step("extract", "active")
            action_items = extract_action_items(transcript)
            decisions = extract_key_decisions(transcript)
            questions = extract_questions(transcript)
            set_step("extract", "done")

            set_step("rag", "active")
            rag_chain = build_rag_chain(transcript)
            set_step("rag", "done")

            st.session_state.result = {
                "title": title,
                "transcript": transcript,
                "summary": summary,
                "action_items": action_items,
                "key_decisions": decisions,
                "open_questions": questions,
                "rag_chain": rag_chain,
            }
            st.session_state.pipeline_done = True
            status_box.success("✅ Analysis complete.")
            time.sleep(0.4)
            status_box.empty()
            st.rerun()

        except Exception as e:
            for k, _, _ in PIPELINE_STEPS:
                if st.session_state.pipeline_steps.get(k) == "active":
                    st.session_state.pipeline_steps[k] = "pending"
            status_box.error(f"❌ Error: {e}")

# ─── Results ──────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    st.markdown(f"""
    <div class="title-strip">
        <div class="tape-eyebrow">📌 Session Title</div>
        <div class="title-text">{r['title']}</div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2], gap="medium")

    with col1:
        st.markdown(f"""
        <div class="tape-card">
            <div class="tape-eyebrow">📋 Summary</div>
            <div class="tape-body">{r['summary']}</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        with st.expander("📝 Full Transcript", expanded=False):
            st.markdown(f'<div class="reel-box">{r["transcript"]}</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown(f"""
        <div class="tape-card">
            <div class="tape-eyebrow">✅ Action Items</div>
            <div class="tape-body">{r['action_items']}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="tape-card">
            <div class="tape-eyebrow">🔑 Key Decisions</div>
            <div class="tape-body">{r['key_decisions']}</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="tape-card">
            <div class="tape-eyebrow">❓ Open Questions</div>
            <div class="tape-body">{r['open_questions']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="deck-sub" style="font-size:0.9rem;color:var(--text);margin-bottom:0.8rem">💬 CHAT WITH YOUR MEETING</div>', unsafe_allow_html=True)

    if st.session_state.chat_history:
        chat_html = '<div class="chat-reel">'
        for msg in st.session_state.chat_history:
            tag_class = "tag-you" if msg["role"] == "user" else "tag-ai"
            tag_text = "You" if msg["role"] == "user" else "🤖 Assistant"
            chat_html += f"""
            <div class="chat-line">
                <span class="chat-tag {tag_class}">{tag_text}</span>
                <span class="chat-text">{msg['content']}</span>
            </div>"""
        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="tape-card" style="text-align:center;padding:2rem">
            <div style="font-size:1.6rem;margin-bottom:0.4rem">💬</div>
            <div style="color:var(--text-muted);font-size:0.82rem">Ask anything about your meeting transcript</div>
        </div>""", unsafe_allow_html=True)

    chat_col1, chat_col2 = st.columns([5, 1], gap="small")
    with chat_col1:
        user_input = st.text_input(
            "Your question",
            placeholder="What were the main decisions made?",
            label_visibility="collapsed",
            key="chat_input_box",
        )
    with chat_col2:
        send_btn = st.button("Send →", use_container_width=True)

    if send_btn and user_input.strip():
        with st.spinner("Thinking…"):
            answer = ask_question(r["rag_chain"], user_input.strip())
        st.session_state.chat_history.append({"role": "user", "content": user_input.strip()})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

else:
    st.markdown("""
    <div class="empty-console">
        <div class="reel-icon"></div>
        <div style="font-family:'Oswald',sans-serif;font-size:1.4rem;font-weight:600;color:var(--text);margin-bottom:0.5rem">
            Ready to Analyse
        </div>
        <div style="color:var(--text-muted);font-size:0.85rem;max-width:380px;line-height:1.7">
            Drop a YouTube URL or local file path in the sidebar, pick a language, and hit <strong>● Analyse</strong> to start rolling.
        </div>
    </div>""", unsafe_allow_html=True)