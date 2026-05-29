"""
Christianity AI Assistant — Streamlit App (Gemini Version)
===========================================================
Run with:  streamlit run app.py
"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Christianity AI Assistant",
    page_icon="✝️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from chat_engine import ChristianChatEngine
from image_gen   import generate_christian_image, SAMPLE_IMAGE_PROMPTS
from denomination_handler import list_denominations, DENOMINATIONS
from safety import check_text_safety, SafetyLevel


# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');

  html, body, [data-testid="stAppViewContainer"] {
    background: #0f0d0a;
    color: #e8dcc8;
  }
  [data-testid="stSidebar"] {
    background: #1a1610;
    border-right: 1px solid #3a3020;
  }
  h1, h2, h3 {
    font-family: 'Cinzel', serif !important;
    color: #c9a84c !important;
    letter-spacing: 0.04em;
  }
  p, li, span, label, div {
    font-family: 'Lora', serif !important;
  }
  .stChatMessage {
    background: #1a1610 !important;
    border: 1px solid #3a3020 !important;
    border-radius: 8px !important;
    margin-bottom: 8px !important;
  }
  .verse-card {
    background: #1e1a12;
    border-left: 3px solid #c9a84c;
    padding: 10px 14px;
    margin: 6px 0;
    border-radius: 4px;
    font-style: italic;
    font-size: 0.9em;
    color: #d4c4a0;
  }
  .verse-ref {
    font-weight: 600;
    font-style: normal;
    color: #c9a84c;
    font-size: 0.85em;
  }
  .valid-badge   { color: #5cb85c; font-size: 0.8em; }
  .invalid-badge { color: #d9534f; font-size: 0.8em; }
  .warn-box {
    background: #2a2010;
    border: 1px solid #c9a84c;
    border-radius: 6px;
    padding: 10px 14px;
    color: #f0d070;
    font-size: 0.9em;
    margin: 8px 0;
  }
  .block-box {
    background: #2a1010;
    border: 1px solid #d9534f;
    border-radius: 6px;
    padding: 10px 14px;
    color: #f07070;
    font-size: 0.9em;
    margin: 8px 0;
  }
  .fallback-box {
    background: #12201a;
    border: 1px solid #5cb85c;
    border-radius: 6px;
    padding: 12px 16px;
    color: #a0d4b0;
    font-size: 0.95em;
    font-style: italic;
    margin: 8px 0;
  }
  .stButton button {
    background: #c9a84c !important;
    color: #0f0d0a !important;
    border: none !important;
    font-family: 'Cinzel', serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em;
  }
  .stButton button:hover { background: #e0c070 !important; }
  .stTextInput input, .stTextArea textarea {
    background: #1a1610 !important;
    color: #e8dcc8 !important;
    border-color: #3a3020 !important;
  }
  hr { border-color: #3a3020 !important; }
  .denom-badge {
    display: inline-block;
    background: #2a2010;
    border: 1px solid #c9a84c;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.8em;
    color: #c9a84c;
    margin-bottom: 8px;
  }
  .gemini-badge {
    display: inline-block;
    background: #102030;
    border: 1px solid #4a9ade;
    border-radius: 20px;
    padding: 2px 12px;
    font-size: 0.75em;
    color: #4a9ade;
  }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
if "engine"       not in st.session_state:
    st.session_state.engine       = ChristianChatEngine()
if "messages"     not in st.session_state:
    st.session_state.messages     = []
if "denomination" not in st.session_state:
    st.session_state.denomination = "General / Ecumenical"
if "tab"          not in st.session_state:
    st.session_state.tab          = "chat"


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ✝️ Christianity AI")
    st.markdown(
        '<span class="gemini-badge">⚡ Powered by Gemini-3-flash-preview</span>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    st.markdown("### 📖 Your Tradition")
    denom_names = list_denominations()
    selected = st.selectbox(
        "Denomination",
        denom_names,
        index=denom_names.index(st.session_state.denomination),
        label_visibility="collapsed",
    )
    if selected != st.session_state.denomination:
        st.session_state.denomination = selected

    profile = DENOMINATIONS[selected]
    st.markdown(
        f'<div class="denom-badge">{profile.emoji} {profile.short}</div>',
        unsafe_allow_html=True,
    )
    st.caption(profile.description)

    st.markdown("---")
    st.markdown("### 🗂️ Mode")
    if st.button("💬 Chat",             use_container_width=True): st.session_state.tab = "chat";  st.rerun()
    if st.button("🎨 Generate Image",   use_container_width=True): st.session_state.tab = "image"; st.rerun()
    if st.button("🧪 Evaluation Tests", use_container_width=True): st.session_state.tab = "eval";  st.rerun()

    st.markdown("---")
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.engine.clear_history()
        st.rerun()

    st.markdown("---")
    st.caption("Free Gemini API · ChromaDB · KJV Bible RAG")

    # API key status
    key = os.getenv("GEMINI_API_KEY", "")
    if key:
        st.success("✅ Gemini API key loaded")
    else:
        st.error("❌ GEMINI_API_KEY missing in .env")


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align:center;margin-bottom:4px;'>✝ Christianity AI Assistant</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center;color:#8a7a5a;font-style:italic;margin-top:0'>"
    "Scripture-grounded · Denomination-aware · Hallucination-safe · Free Gemini API"
    "</p>",
    unsafe_allow_html=True,
)
st.markdown("---")


# ════════════════════════════════════════════════════════════════════════════
# HELPER: render one assistant message
# ════════════════════════════════════════════════════════════════════════════
def render_assistant_msg(msg: dict):
    if msg.get("safety_blocked"):
        st.markdown(
            f'<div class="block-box">🚫 {msg["content"]}</div>',
            unsafe_allow_html=True,
        )
        return

    if msg.get("safety_warning"):
        st.markdown(
            f'<div class="warn-box">⚠️ {msg.get("safety_message","")}</div>',
            unsafe_allow_html=True,
        )

    st.markdown(msg["content"])

    if msg.get("verses_used"):
        with st.expander("📖 Scripture references used", expanded=False):
            for v in msg["verses_used"]:
                st.markdown(
                    f'<div class="verse-card">'
                    f'<span class="verse-ref">{v["reference"]}</span><br>{v["text"]}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    if msg.get("verse_checks"):
        invalid = [c for c in msg["verse_checks"] if not c["valid"]]
        valid   = [c for c in msg["verse_checks"] if  c["valid"]]
        with st.expander(
            f"🔍 Verse verification  {len(valid)}✅  {len(invalid)}❌",
            expanded=bool(invalid),
        ):
            for c in msg["verse_checks"]:
                badge = (
                    '<span class="valid-badge">✅ Verified</span>'
                    if c["valid"] else
                    '<span class="invalid-badge">❌ Not in Bible</span>'
                )
                st.markdown(f"**{c['reference']}** — {badge}", unsafe_allow_html=True)
                if c["valid"] and c.get("text"):
                    st.caption(c["text"])


# ════════════════════════════════════════════════════════════════════════════
# TAB: CHAT
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.tab == "chat":

    # Render history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            # ✅ FIXED: explicit if/else instead of ternary to avoid magic-write bug
            if msg["role"] == "assistant":
                render_assistant_msg(msg)
            else:
                st.markdown(msg["content"])

    # Starter prompts (shown when chat is empty)
    if not st.session_state.messages:
        st.markdown("### ✨ Try asking…")
        starters = [
            "What does the Bible say about forgiveness?",
            "Explain the Trinity simply",
            "Write a short morning prayer",
            "What is the fruit of the Spirit?",
            "Who wrote the book of Psalms?",
        ]
        cols = st.columns(len(starters))
        for col, prompt in zip(cols, starters):
            if col.button(prompt, use_container_width=True):
                st.session_state._auto_prompt = prompt
                st.rerun()

    # Handle starter button click
    if hasattr(st.session_state, "_auto_prompt"):
        user_input = st.session_state._auto_prompt
        del st.session_state._auto_prompt
    else:
        user_input = st.chat_input("Ask about Christianity, theology, or the Bible…")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("🙏 Searching scripture…"):
                result = st.session_state.engine.chat(
                    user_input,
                    denomination=st.session_state.denomination,
                )

            msg = {
                "role":           "assistant",
                "content":         result["response"],
                "safety_blocked":  result["safety_blocked"],
                "safety_warning":  result["safety_warning"],
                "safety_message":  result["safety_message"],
                "verses_used":     result["verses_used"],
                "verse_checks":    result["verse_checks"],
            }
            render_assistant_msg(msg)

        st.session_state.messages.append(msg)


# ════════════════════════════════════════════════════════════════════════════
# TAB: IMAGE GENERATION
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.tab == "image":
    st.markdown("## 🎨 Generate Christian Imagery")
    st.markdown(
        "Generate reverent Christian artwork via **Gemini Imagen 3** (free tier). "
        "If Imagen is unavailable in your region, a vivid text description is provided instead."
    )
    st.info(
        "💡 **Gemini Imagen 3** may not be available in all regions on the free tier. "
        "If unavailable, the app automatically falls back to a detailed AI art description.",
        icon="ℹ️",
    )
    st.markdown("---")

    col1, col2 = st.columns([2, 1])

    with col1:
        image_prompt = st.text_area(
            "Describe the image:",
            placeholder="e.g. The Good Shepherd carrying a lamb at golden hour",
            height=100,
        )

        if st.button("✨ Generate", use_container_width=True):
            if image_prompt.strip():
                with st.spinner("🎨 Creating artwork…"):
                    result = generate_christian_image(image_prompt)

                if result["blocked"]:
                    st.markdown(
                        f'<div class="block-box">🚫 {result["message"]}</div>',
                        unsafe_allow_html=True,
                    )
                elif result["success"]:
                    if result.get("image_bytes"):
                        st.image(result["image_bytes"], caption=image_prompt, use_column_width=True)
                        st.success("✅ Image generated with Imagen 3")
                    elif result.get("fallback"):
                        st.markdown("**🖼️ AI Art Description** *(Imagen unavailable — text fallback)*")
                        st.markdown(
                            f'<div class="fallback-box">{result["message"]}</div>',
                            unsafe_allow_html=True,
                        )
                        st.caption("Tip: Copy this description into Canva AI, Adobe Firefly, or Bing Image Creator to generate the image.")
                    elif result.get("url"):
                        st.image(result["url"], caption=image_prompt, use_column_width=True)
                else:
                    st.error(result["message"])
            else:
                st.warning("Please enter an image description.")

    with col2:
        st.markdown("#### 💡 Sample prompts")
        for prompt in SAMPLE_IMAGE_PROMPTS:
            if st.button(prompt, use_container_width=True, key=f"img_{prompt[:25]}"):
                with st.spinner("🎨 Creating artwork…"):
                    result = generate_christian_image(prompt)
                if result["blocked"]:
                    st.markdown(f'<div class="block-box">🚫 {result["message"]}</div>', unsafe_allow_html=True)
                elif result["success"]:
                    if result.get("image_bytes"):
                        st.image(result["image_bytes"], caption=prompt)
                    elif result.get("fallback"):
                        st.markdown(f'<div class="fallback-box">{result["message"]}</div>', unsafe_allow_html=True)
                    elif result.get("url"):
                        st.image(result["url"], caption=prompt)
                else:
                    st.error(result["message"])


# ════════════════════════════════════════════════════════════════════════════
# TAB: EVALUATION
# ════════════════════════════════════════════════════════════════════════════
elif st.session_state.tab == "eval":
    import json, pandas as pd

    st.markdown("## 🧪 Evaluation Test Suite")
    st.markdown(
        "20 test cases covering hallucination, adversarial prompts, "
        "fake verses, theological edge cases, and denomination accuracy."
    )
    st.markdown("---")

    with open("eval_dataset.json", "r") as f:
        eval_cases = json.load(f)

    categories = list({c["category"] for c in eval_cases})
    selected_cats = st.multiselect("Filter by category:", categories, default=categories)
    filtered = [c for c in eval_cases if c["category"] in selected_cats]
    st.markdown(f"**{len(filtered)} test cases selected**")

    if st.button("▶️ Run Safety Layer Tests", use_container_width=True):
        results = []
        progress = st.progress(0)
        for i, case in enumerate(filtered):
            safety = check_text_safety(case["input"])
            is_blocked = safety.level == SafetyLevel.BLOCKED
            passed = (is_blocked == case["should_block"])
            results.append({
                "ID":          case["id"],
                "Category":    case["category"],
                "Description": case["description"],
                "Blocked?":    "✅ Yes" if is_blocked else "❌ No",
                "Expected":    "Block" if case["should_block"] else "Allow",
                "Result":      "✅ PASS" if passed else "❌ FAIL",
                "Severity":    case["severity"],
            })
            progress.progress((i + 1) / len(filtered))

        df = pd.DataFrame(results)
        passed_n = sum(1 for r in results if r["Result"] == "✅ PASS")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Tests", len(results))
        col2.metric("Passed", passed_n)
        col3.metric("Failed", len(results) - passed_n)
        st.dataframe(df, use_container_width=True)

    else:
        df = pd.DataFrame([{
            "ID":           c["id"],
            "Category":     c["category"],
            "Description":  c["description"],
            "Should Block": "Yes" if c["should_block"] else "No",
            "Severity":     c["severity"],
            "Test Input":   c["input"][:60] + "…" if len(c["input"]) > 60 else c["input"],
        } for c in filtered])
        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        st.markdown("#### 📋 Full test case details")
        for case in filtered:
            with st.expander(f"[{case['id']}] {case['description']}"):
                st.markdown(f"**Input:** `{case['input']}`")
                st.markdown(f"**Expected behavior:** {case['expected_behavior']}")
                st.markdown(f"**Should block:** {'🚫 Yes' if case['should_block'] else '✅ No'}")
                st.markdown(f"**Severity:** `{case['severity']}`")