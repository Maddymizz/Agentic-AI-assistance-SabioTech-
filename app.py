# app.py
import streamlit as st
from agent import run_agent

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SabioTech",
    page_icon="💻",
    layout="wide"
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .action-badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }
    .badge-search  { background: #dcfce7; color: #166534; }
    .badge-code    { background: #fef9c3; color: #713f12; }
    .badge-general { background: #e0e7ff; color: #3730a3; }
    .history-item {
        padding: 8px 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        font-size: 0.85rem;
        cursor: pointer;
        border: 1px solid #e5e7eb;
        transition: background 0.15s;
    }
    .history-item:hover { background: #f3f4f6; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

# ── Layout ─────────────────────────────────────────────────────────────────
col_main, col_sidebar = st.columns([2.5, 1])

# ── Sidebar: History ─────────────────────────────────────────────────────────
with col_sidebar:
    st.markdown("### 📋 Conversation History")

    if not st.session_state.history:
        st.caption("No history yet. Ask something!")
    else:
        if st.button("🗑 Clear History", use_container_width=True):
            st.session_state.history = []
            st.rerun()

        for i, item in enumerate(reversed(st.session_state.history)):
            action = item.get("action", "general")
            icon = {"search": "🔍", "code": "💻", "general": "💬"}.get(action, "💬")
            with st.expander(f"{icon} {item['question'][:40]}...", expanded=False):
                st.markdown(f"**Answer:** {item['answer'][:200]}...")
                st.caption(f"Tool used: {action}")

# ── Main panel ────────────────────────────────────────────────────────────────
with col_main:
    st.markdown('<div class="main-header">🔍SabioTech AI Portal</div>', unsafe_allow_html=True)
    st.caption("Powered by Groq (Llama 3) + Tavily Search + Python Execution")

    st.markdown("---")

    # Example prompts
    st.markdown("**Try these examples:**")
    examples = [
        "What is the current price of Bitcoin?",
        "Calculate compound interest on ₹50,000 at 8% for 10 years",
        "What happened in AI news this week?",
        "Generate the first 20 Fibonacci numbers",
    ]
    cols = st.columns(2)
    for i, ex in enumerate(examples):
        with cols[i % 2]:
            if st.button(ex, use_container_width=True):
                st.session_state["prefill"] = ex

    st.markdown("---")

    # Input
    default_val = st.session_state.pop("prefill", "")
    question = st.text_area(
        "Your question",
        value=default_val,
        placeholder="Ask anything — I'll search the web, write code, or answer directly.",
        height=100,
        label_visibility="collapsed"
    )

    run_btn = st.button("▶ Run Agent", type="primary", use_container_width=True)

    # ── Agent execution ──────────────────────────────────────────────────────
    if run_btn and question.strip():
        with st.spinner("Agent thinking..."):
            try:
                result = run_agent(question, st.session_state.history)
            except Exception as e:
                st.error(f"Agent error: {str(e)}")
                st.stop()

        action = result.get("action", "general")
        badge_class = f"badge-{action}"
        label = {"search": "🔍 Web Search", "code": "💻 Code Execution", "general": "💬 Direct Answer"}.get(action, "💬 Direct Answer")

        st.markdown(f'<span class="action-badge {badge_class}">{label}</span>', unsafe_allow_html=True)

        # Answer
        st.markdown("### Answer")
        st.markdown(result["answer"])

        # Code + output (if applicable)
        if result.get("code"):
            st.markdown("### Generated Code")
            st.code(result["code"], language="python")

        if result.get("execution_output"):
            st.markdown("### Execution Output")
            st.success(result["execution_output"])

        # Sources
        if result.get("sources"):
            st.markdown("### Sources")
            for s in result["sources"]:
                if s:
                    st.markdown(f"- {s}")

        # Save to history
        st.session_state.history.append({
            "question": question,
            "answer": result["answer"],
            "action": action
        })

    elif run_btn:
        st.warning("Please enter a question first.")