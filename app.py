"""
AI Assistant Builder - Main Entry Point (v2.1)
Premium SaaS UI/UX with modern dark-mode design.
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
# GLOBAL STYLES & THEME
# ========================

CUSTOM_CSS = """
<style>
/* Color scheme */
:root {
    --bg-primary: #0f0f0f;
    --bg-secondary: #1a1a1a;
    --bg-tertiary: #2d2d2d;
    --text-primary: #e0e0e0;
    --text-secondary: #a0a0a0;
    --accent: #6366f1;
    --accent-light: #818cf8;
    --success: #10b981;
    --danger: #ef4444;
    --border: #333333;
}

/* Global font & spacing */
body, html {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
                 'Ubuntu', 'Cantarell', sans-serif;
}

/* Card styling */
.card {
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease;
}

.card:hover {
    border-color: var(--accent);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
    transform: translateY(-2px);
}

/* Metric cards */
[data-testid="metric-container"] {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 20px !important;
    transition: all 0.3s ease !important;
}

[data-testid="metric-container"]:hover {
    border-color: var(--accent) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15) !important;
}

/* Button styling */
.stButton > button {
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 4px rgba(99, 102, 241, 0.3) !important;
}

.stButton > button:hover {
    background: var(--accent-light) !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4) !important;
    transform: translateY(-1px) !important;
}

/* Input fields */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > select,
.stNumberInput > div > div > input {
    background: var(--bg-tertiary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    transition: all 0.3s ease !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div > select:focus,
.stNumberInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
}

/* Tabs styling */
[data-testid="stTabs"] [role="tablist"] button {
    border-radius: 8px !important;
    margin-right: 8px !important;
    transition: all 0.3s ease !important;
}

[data-testid="stTabs"] [role="tablist"] button[aria-selected="true"] {
    background: var(--accent) !important;
    color: white !important;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3) !important;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: var(--bg-primary) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] > div > div:first-child {
    padding: 20px !important;
}

/* Divider */
.stDivider {
    border-color: var(--border) !important;
}

/* Expander */
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

/* Message styling */
.stChatMessage {
    border-radius: 12px !important;
    padding: 16px !important;
    border: 1px solid var(--border) !important;
}

/* Success/Error alerts */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    border: 1px solid var(--border) !important;
}

/* Gradient text */
.gradient-text {
    background: linear-gradient(135deg, var(--accent), var(--accent-light));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
}

/* Badge styling */
.badge {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    background: var(--bg-tertiary);
    border: 1px solid var(--border);
    color: var(--text-primary);
}

.badge-success {
    background: rgba(16, 185, 129, 0.1);
    border-color: #10b981;
    color: #10b981;
}

.badge-danger {
    background: rgba(239, 68, 68, 0.1);
    border-color: #ef4444;
    color: #ef4444;
}

.badge-accent {
    background: rgba(99, 102, 241, 0.1);
    border-color: var(--accent);
    color: var(--accent);
}

/* Status indicator */
.status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 6px;
}

.status-dot.online {
    background: #10b981;
    box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
}

.status-dot.offline {
    background: #ef4444;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .card {
        padding: 16px;
    }
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

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
    st.Page("assistants.py", title="Assistants", icon="👥"),
    st.Page("chat.py", title="Chat", icon="💬"),
    st.Page("settings.py", title="Settings", icon="⚙️"),
]

pg = st.navigation(pages)

# ========================
# APP HEADER & SIDEBAR
# ========================

# Premium header
st.sidebar.markdown(
    """
    <div style="padding: 12px 0;">
        <span class="gradient-text" style="font-size: 1.4rem;">🤖 AI Assistant Builder</span>
        <br>
        <span style="color: var(--text-secondary); font-size: 0.85rem;">v2.1 • Multi-backend AI</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.divider()

# Show username if set
if st.session_state.get("username"):
    st.sidebar.markdown(
        f"""
        <div style="background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; padding: 12px; margin-bottom: 12px;">
            <span style="font-size: 0.9rem; color: var(--text-secondary);">Logged in as</span><br>
            <span style="color: var(--accent); font-weight: 600;">👤 {st.session_state.username}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

# Backend status indicators - modern pills
st.sidebar.markdown("<span style='color: var(--text-secondary); font-size: 0.85rem; font-weight: 600;'>BACKEND STATUS</span>", unsafe_allow_html=True)

from ai_helper import check_ollama_connection

col1, col2, col3, col4 = st.sidebar.columns(4, gap="small")
backends_config = [
    ("Ollama", "🦙", check_ollama_connection()),
    ("Claude", "🤖", bool(st.session_state.get("claude_key"))),
    ("ChatGPT", "💬", bool(st.session_state.get("openai_key"))),
    ("Grok", "⚡", bool(st.session_state.get("grok_key"))),
]

with col1:
    name, icon, status = backends_config[0]
    status_color = "success" if status else "danger"
    st.markdown(
        f"""<div class="badge badge-{status_color}"><span class="status-dot {'online' if status else 'offline'}"></span>{icon} {name}</div>""",
        unsafe_allow_html=True
    )

with col2:
    name, icon, status = backends_config[1]
    status_color = "success" if status else "danger"
    st.markdown(
        f"""<div class="badge badge-{status_color}"><span class="status-dot {'online' if status else 'offline'}"></span>{icon} {name}</div>""",
        unsafe_allow_html=True
    )

with col3:
    name, icon, status = backends_config[2]
    status_color = "success" if status else "danger"
    st.markdown(
        f"""<div class="badge badge-{status_color}"><span class="status-dot {'online' if status else 'offline'}"></span>{icon} {name}</div>""",
        unsafe_allow_html=True
    )

with col4:
    name, icon, status = backends_config[3]
    status_color = "success" if status else "danger"
    st.markdown(
        f"""<div class="badge badge-{status_color}"><span class="status-dot {'online' if status else 'offline'}"></span>{icon} {name}</div>""",
        unsafe_allow_html=True
    )

st.sidebar.divider()

# About section
st.sidebar.markdown("""
#### 📚 About

Premium no-code AI assistant builder with **local & cloud models**.

**Supported Backends:**
- 🦙 Ollama (local)
- 🤖 Claude (Anthropic)
- 💬 ChatGPT (OpenAI)
- ⚡ Grok (xAI)

**Key Features:**
- ✨ Multi-backend chat
- 📖 RAG with PDF/TXT uploads
- 💾 Export/Import assistants
- 👤 User profiles & storage
- 📊 Usage analytics
- 🚀 One-click deployments

---
*Made with ❤️ for builders*
""")

# ========================
# RUN CURRENT PAGE
# ========================

pg.run()
