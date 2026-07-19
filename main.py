import re
from datetime import datetime
from html import escape as html_escape

import streamlit as st

from ingestion.splitter import Splitter
from ingestion.loader import load
from rag.vector_store import create_vectorstore
from rag.chain import rag_chain
from rag.retriver import Retriver
from langchain_core import chat_history
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

st.set_page_config(
    page_title="TubeMind AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Injected stylesheet without any blank lines to prevent Markdown escaping
st.markdown("""<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet"><style>
:root {
    --bg: #0a0b10;
    --surface: rgba(255,255,255,0.035);
    --surface-2: rgba(255,255,255,0.07);
    --surface-hover: rgba(255,255,255,0.1);
    --border: rgba(255,255,255,0.09);
    --border-soft: rgba(255,255,255,0.06);
    --text: #ece9e2;
    --text-muted: #8b8f9c;
    --text-faint: #565b6b;
    --amber: #f2a93b;
    --amber-dim: rgba(242,169,59,0.14);
    --teal: #2dd4bf;
    --teal-dim: rgba(45,212,191,0.14);
    --radius: 14px;
    --radius-sm: 9px;
}
html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif;
    color: var(--text);
}
.main .block-container {
    background: radial-gradient(circle at 15% 0%, rgba(242,169,59,0.06), transparent 45%), radial-gradient(circle at 88% 10%, rgba(45,212,191,0.05), transparent 45%), var(--bg);
    max-width: 1050px;
    padding-top: 3.5rem !important;
    padding-bottom: 5rem !important;
}
#MainMenu, footer { visibility: hidden; }
header { background: transparent !important; }
.letterbox-top, .letterbox-bottom {
    position: fixed; left: 0; right: 0; height: 24px;
    background: #000; z-index: 99999; pointer-events: none;
    display: flex; align-items: center;
    font-family: 'JetBrains Mono', monospace; font-size: 10px;
    letter-spacing: 1.5px; color: rgba(255,255,255,0.3);
}
.letterbox-top { top: 0; padding: 0 20px; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.08); }
.letterbox-bottom { bottom: 0; padding: 0 20px; justify-content: space-between; border-top: 1px solid rgba(255,255,255,0.08); }
.letterbox-top span:last-child, .letterbox-bottom span:last-child { color: var(--amber); }
[data-testid="stSidebar"] {
    background-color: #0c0e14 !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebarContent"]::after {
    content: "";
    position: absolute;
    top: 0; right: 0; bottom: 0; width: 4px;
    background-image: repeating-linear-gradient(to bottom, rgba(242,169,59,0.3) 0px, rgba(242,169,59,0.3) 6px, transparent 6px, transparent 18px);
    z-index: 10;
}
.brand-row { display: flex; align-items: center; gap: 12px; padding-top: 10px; }
.brand-mark {
    width: 38px; height: 38px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, var(--amber), #d9832a);
    box-shadow: 0 0 20px rgba(242,169,59,0.3); font-size: 18px;
}
.brand-name { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1.25rem; }
.brand-tag {
    font-family: 'JetBrains Mono', monospace; font-size: 9.5px; color: var(--text-faint);
    letter-spacing: 1.5px; margin: 4px 0 20px 50px; text-transform: uppercase;
}
.side-heading {
    font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 1.5px;
    text-transform: uppercase; color: var(--text-muted); margin: 20px 0 12px 2px;
    display: flex; align-items: center; gap: 8px;
}
.side-heading::after { content: ""; flex: 1; height: 1px; background: var(--border-soft); }
.stTextInput input {
    background-color: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
}
.stTextInput input:focus { border-color: var(--amber) !important; }
button[aria-label="Load video"], button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, var(--amber), #d9832a) !important;
    color: #14100a !important;
    border: none !important;
    font-weight: 600 !important;
}
.hero-wrap { text-align: center; padding: 40px 10px; position: relative; }
.hero-mark {
    width: 64px; height: 64px; margin: 0 auto 16px auto; border-radius: 16px;
    display: flex; align-items: center; justify-content: center; font-size: 26px;
    background: linear-gradient(135deg, var(--amber), #d9832a);
    box-shadow: 0 0 35px rgba(242,169,59,0.25);
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 2.5rem;
    background: linear-gradient(90deg, #ffffff, var(--teal));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 12px;
}
.hero-subtitle { color: var(--text-muted); font-size: 1rem; max-width: 540px; margin: 0 auto 12px auto; line-height: 1.5; }
.hero-pipeline { font-family: 'JetBrains Mono', monospace; font-size: 10.5px; color: var(--teal); letter-spacing: 1.2px; margin-bottom: 30px; }
.feature-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; max-width: 850px; margin: 0 auto; }
.feature-card { background: var(--surface); border: 1px solid var(--border-soft); border-radius: var(--radius); padding: 20px 16px; }
.feature-icon { font-size: 18px; margin-bottom: 8px; width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; background: var(--surface-2); }
.feature-title { font-weight: 600; font-size: 14px; margin-bottom: 4px; font-family: 'Space Grotesk', sans-serif; }
.feature-desc { color: var(--text-muted); font-size: 12px; line-height: 1.5; }
.video-header {
    display: flex; gap: 20px; align-items: center; background: var(--surface);
    border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; margin-bottom: 24px;
    position: relative; overflow: hidden;
}
.video-header::before { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; background: linear-gradient(to bottom, var(--amber), var(--teal)); }
.video-title { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1.25rem; margin-bottom: 6px; }
.status-pill {
    display: inline-flex; align-items: center; gap: 6px; font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600;
    color: var(--teal); background: var(--teal-dim); border: 1px solid rgba(45,212,191,0.25); padding: 2px 10px; border-radius: 999px;
}
.status-pill .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--teal); }
.video-meta-row { display: flex; flex-wrap: wrap; gap: 16px; margin-top: 12px; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--text-muted); }
.chip-label { font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 1px; text-transform: uppercase; color: var(--text-faint); margin-bottom: 8px; }
[data-testid="stChatMessage"] {
    background-color: var(--surface) !important;
    border: 1px solid var(--border-soft) !important;
    border-radius: 10px !important;
}
.msg-header { font-family: 'JetBrains Mono', monospace; font-size: 10px; margin-bottom: 4px; display: flex; gap: 10px; }
.msg-role.user { color: var(--amber); font-weight: 600; }
.msg-role.assistant { color: var(--teal); font-weight: 600; }
.msg-time { color: var(--text-faint); }
.custom-footer { text-align: center; margin-top: 50px; padding-top: 20px; border-top: 1px solid var(--border-soft); color: var(--text-faint); font-family: 'JetBrains Mono', monospace; font-size: 11px; }
</style>
<div class="letterbox-top"><span>TUBEMIND AI · REC ●</span><span>00:00:00:00</span></div>
<div class="letterbox-bottom"><span>TRANSCRIPT → VECTORS → ANSWERS</span><span>16:9</span></div>
""", unsafe_allow_html=True)

if "library" not in st.session_state:
    st.session_state.library = {}
if "active_id" not in st.session_state:
    st.session_state.active_id = None

def extract_video_id(url: str) -> str:
    match = re.search(r"(?:v=|/embed/|/shorts/|youtu\.be/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else url.strip()

def now_stamp() -> str:
    return datetime.now().strftime("%H:%M")

def chat_transcript_md(title: str, messages: list) -> str:
    lines = [f"# {title}", ""]
    for m in messages:
        speaker = "You" if m["role"] == "user" else "TubeMind AI"
        lines.append(f"**[{m['time']}] {speaker}:** {m['content']}")
        lines.append("")
    return "\n".join(lines)

SUGGESTIONS = [
    ("📝 Summarize", "Summarize this video in a concise overview."),
    ("🔑 Key takeaways", "What are the key takeaways from this video?"),
    ("🗂️ Main topics", "List and briefly explain the main topics discussed in this video."),
    ("⏱️ Walk me through it", "Walk me through this video in chronological order."),
]

with st.sidebar:
    st.markdown("""
    <div class="brand-row">
        <div class="brand-mark">🎬</div>
        <div class="brand-name">TubeMind AI</div>
    </div>
    <div class="brand-tag">Transcript → vectors → answers</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="side-heading">New video</div>', unsafe_allow_html=True)
    link = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=…",
        label_visibility="collapsed",
    )

    if link:
        try:
            preview_thumb = load.thumbnailLoader(link)
            st.image(preview_thumb, use_container_width=True)
        except Exception:
            pass

    load_clicked = st.button("Load video", type="primary", use_container_width=True, key="load_video_btn")
    st.caption("Works best with public videos that have captions available.")

    if load_clicked:
        if not link.strip():
            st.error("Please paste a YouTube URL first.")
        else:
            vid_id = extract_video_id(link)

            if vid_id in st.session_state.library:
                st.session_state.active_id = vid_id
                st.toast("Already in your library — switched to it.", icon="🔁")
                st.rerun()
            else:
                try:
                    with st.status("Processing video…", expanded=True) as status:
                        status.write("00:00  Fetching transcript…")
                        transcript = load.videoLoader(link)
                        heading = load.titleLoader(link)

                        try:
                            thumbnail = load.thumbnailLoader(link)
                        except Exception:
                            thumbnail = None

                        status.write("00:01  Splitting transcript into chunks…")
                        chunks = Splitter.split(transcript)

                        status.write("00:02  Embedding chunks into a vector store…")
                        vector_storage = create_vectorstore(chunks)

                        status.write("00:03  Building the retriever…")
                        retriever = Retriver.create_retriver(vector_storage)

                        status.write("00:04  Wiring up the RAG chain…")
                        final_chain = rag_chain(retriever)

                        status.update(label="Video ready", state="complete", expanded=False)

                    st.session_state.library[vid_id] = {
                        "url": link,
                        "title": heading,
                        "thumbnail": thumbnail,
                        "chain": final_chain,
                        "messages": [],
                        "chunks": len(chunks),
                        "loaded_at": datetime.now().strftime("%b %d, %H:%M"),
                    }
                    st.session_state.active_id = vid_id
                    st.toast(f"“{heading}” is ready to chat with.", icon="✅")
                    st.rerun()

                except Exception as e:
                    st.error(f"Could not process this video — {e}")

    st.markdown('<div class="side-heading">Your videos</div>', unsafe_allow_html=True)

    if not st.session_state.library:
        st.caption("Nothing loaded yet — paste a link above to get started.")
    else:
        for vid_id, data in st.session_state.library.items():
            is_active = vid_id == st.session_state.active_id
            
            c_title, c_remove = st.columns([4, 1])
            with c_title:
                label = data["title"] if len(data["title"]) <= 30 else data["title"][:29] + "…"
                if st.button(
                    ("● " if is_active else "") + label,
                    key=f"switch_{vid_id}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                ):
                    st.session_state.active_id = vid_id
                    st.rerun()
            with c_remove:
                if st.button("✕", key=f"remove_{vid_id}", use_container_width=True):
                    del st.session_state.library[vid_id]
                    if st.session_state.active_id == vid_id:
                        remaining = list(st.session_state.library.keys())
                        st.session_state.active_id = remaining[0] if remaining else None
                    st.rerun()

active = st.session_state.library.get(st.session_state.active_id)

if active is None:
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-mark">🎬</div>
        <div class="hero-title">TubeMind AI</div>
        <div class="hero-subtitle">Turn any YouTube video into an intelligent conversation. Paste a link in the sidebar and start asking questions.</div>
        <div class="hero-pipeline">TRANSCRIPT → CHUNKS → EMBEDDINGS → RETRIEVER → CHAT</div>
    </div>
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">📼</div>
            <div class="feature-title">Full transcript ingest</div>
            <div class="feature-desc">Pulls the entire spoken transcript the moment you load a link — nothing to copy-paste.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🧩</div>
            <div class="feature-title">Chunked &amp; embedded</div>
            <div class="feature-desc">Splits the transcript and indexes it into a vector store built for fast retrieval.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">💬</div>
            <div class="feature-title">Grounded answers</div>
            <div class="feature-desc">Ask anything — every answer is retrieved straight out of the video, not guessed.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

else:
    header_col1, header_col2 = st.columns([1, 4])
    
    with header_col1:
        if active["thumbnail"]:
            st.image(active["thumbnail"], use_container_width=True)
        else:
            st.markdown('<div style="background:#161922; aspect-ratio:16/9; border-radius:8px;"></div>', unsafe_allow_html=True)
            
    with header_col2:
        st.markdown(f"""
        <div style="padding-left: 5px;">
            <div class="video-title">{html_escape(active["title"])}</div>
            <span class="status-pill"><span class="dot"></span>Ready</span>
            <div class="video-meta-row">
                <span>⏱ loaded {active['loaded_at']}</span>
                <span>🧩 {active['chunks']} chunks indexed</span>
                <span>💬 {len(active['messages'])} messages</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    a1, a2, a3, _ = st.columns([1.2, 1.2, 1.4, 3.2])
    with a1:
        if st.button("🗑️ Clear chat", use_container_width=True, disabled=len(active["messages"]) == 0):
            active["messages"] = []
            st.rerun()
    with a2:
        st.download_button(
            "⬇ Export chat",
            data=chat_transcript_md(active["title"], active["messages"]),
            file_name=f"{active['title'][:40].strip() or 'chat'}.md",
            mime="text/markdown",
            use_container_width=True,
            disabled=len(active["messages"]) == 0,
        )
    with a3:
        if st.button("✕ Remove video", use_container_width=True, key="main_remove_btn"):
            del st.session_state.library[st.session_state.active_id]
            remaining = list(st.session_state.library.keys())
            st.session_state.active_id = remaining[0] if remaining else None
            st.rerun()

    st.markdown('<div class="chip-label">Quick questions</div>', unsafe_allow_html=True)
    pending_query = None
    chip_cols = st.columns(len(SUGGESTIONS))
    for col, (label, prompt_text) in zip(chip_cols, SUGGESTIONS):
        with col:
            if st.button(label, key=f"chip_{active['url']}_{label}", use_container_width=True):
                pending_query = prompt_text

    st.markdown("### Chat with this video")

    for msg in active["messages"]:
        avatar = "🧑" if msg["role"] == "user" else "🎬"
        role_label = "You" if msg["role"] == "user" else "TubeMind AI"
        role_class = "user" if msg["role"] == "user" else "assistant"
        
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(
                f'<div class="msg-header">'
                f'<span class="msg-role {role_class}">{role_label}</span>'
                f'<span class="msg-time">{msg["time"]}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.markdown(msg["content"])

    typed_query = st.chat_input("Ask something about this video…")
    final_query = typed_query or pending_query

    if final_query:
        stamp = now_stamp()
        active["messages"].append({"role": "user", "content": final_query, "time": stamp})
        
        with st.chat_message("user", avatar="🧑"):
            st.markdown(
                f'<div class="msg-header"><span class="msg-role user">You</span><span class="msg-time">{stamp}</span></div>',
                unsafe_allow_html=True,
            )
            st.markdown(final_query)

        with st.chat_message("assistant", avatar="🎬"):
            assistant_header = st.empty()
            assistant_header.markdown(
                f'<div class="msg-header"><span class="msg-role assistant">TubeMind AI</span><span class="msg-time">{now_stamp()}</span></div>',
                unsafe_allow_html=True,
            )
            with st.spinner("Scanning the transcript…"):
                try:
                    response = active["chain"].invoke(final_query)
                    st.markdown(response)
                    active["messages"].append(
                        {"role": "assistant", "content": response, "time": now_stamp()}
                    )
                    st.rerun()
                except Exception as e:
                    st.error(f"Error generating response: {e}")

st.markdown("""
<div class="custom-footer">TubeMind AI · LangChain + RAG + Streamlit · Built by Darsh Chouhan</div>
""", unsafe_allow_html=True)