"""
No-Code AI Assistant Builder - Main Entry Point (v2.0)
Multi-page navigation using st.Page + st.navigation (Streamlit 2026 best practices).
"""

import streamlit as st

# ========================
# PAGE CONFIGURATION
# ========================

st.set_page_config(
    page_title="AI Assistant Builder",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================
# SESSION STATE INITIALIZATION
# ========================

def init_session_state():
    """Initialize all session state variables."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "current_assistant_id" not in st.session_state:
        st.session_state.current_assistant_id = None
    if "current_model" not in st.session_state:
        st.session_state.current_model = None
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"
    if "claude_key" not in st.session_state:
        st.session_state.claude_key = ""
    if "openai_key" not in st.session_state:
        st.session_state.openai_key = ""
    if "grok_key" not in st.session_state:
        st.session_state.grok_key = ""


init_session_state()

# ========================
# PAGE NAVIGATION (Modern Streamlit)
# ========================

pages = [
    st.Page("home.py", title="Home", icon="🏠"),
    st.Page("create_assistant.py", title="Create", icon="✨"),
    st.Page("assistants.py", title="Assistants", icon="��"),
    st.Page("chat.py", title="Chat", icon="💬"),
    st.Page("settings.py", title="Settings", icon="⚙️"),
]

pg = st.navigation(pages)

# ========================
# APP HEADER & SIDEBAR
# ========================

st.sidebar.markdown("### 🤖 AI Assistant Builder")
st.sidebar.caption("v2.0 | Multi-backend AI Assistant Management")
st.sidebar.divider()

# Show username if set
if st.session_state.get("username"):
    st.sidebar.markdown(f"**👤 {st.session_state.username}**")

# Backend status indicators
from ai_helper import check_ollama_connection

col1, col2, col3, col4 = st.sidebar.columns(4)
with col1:
    status = "🟢" if check_ollama_connection() else "🔴"
    st.caption(f"{status} Ollama")
with col2:
    status = "🟢" if st.session_state.get("claude_key") else "🔴"
    st.caption(f"{status} Claude")
with col3:
    status = "🟢" if st.session_state.get("openai_key") else "🔴"
    st.caption(f"{status} ChatGPT")
with col4:
    status = "🟢" if st.session_state.get("grok_key") else "🔴"
    st.caption(f"{status} Grok")

st.sidebar.divider()

st.sidebar.markdown("""
### About
No-code AI assistant builder with **local & cloud models**.

**Backends:**
- 🦙 Ollama (local)
- 🤖 Claude (Anthropic)
- 💬 ChatGPT (OpenAI)
- ⚡ Grok (xAI)

**Features:**
- Multi-backend chat
- RAG (knowledge base)
- Export/Import
- User profiles
- Usage analytics

[GitHub](https://github.com)
""")

# ========================
# RUN CURRENT PAGE
# ========================

pg.run()
