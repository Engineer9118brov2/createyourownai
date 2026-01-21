"""Home page - Premium Dashboard with analytics and quick test"""
import streamlit as st
import os
import json
from datetime import datetime
from ai_helper import (
    check_ollama_connection,
    list_ollama_models,
    generate_response,
    get_available_backends,
    backend_to_key
)

def load_assistants(username: str = ""):
    """Load assistants from JSON file (per-user if username provided)."""
    file = f"{username.lower()}_assistants.json" if username else "assistants.json"
    if not os.path.exists(file):
        return []
    try:
        with open(file, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def get_recent_activity(username: str = "", limit: int = 5):
    """Get recent assistants created."""
    assistants = load_assistants(username)
    if not assistants:
        return []
    # Sort by created_at descending
    sorted_assistants = sorted(
        assistants,
        key=lambda x: x.get("created_at", ""),
        reverse=True
    )
    return sorted_assistants[:limit]

def render():
    """Render premium dashboard."""
    # Header
    st.markdown(
        """
        <div style="margin-bottom: 30px;">
            <h1 style="margin: 0 0 8px 0;">🎯 Welcome Back</h1>
            <p style="color: var(--text-secondary); margin: 0;">Build powerful AI assistants with local & cloud models</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    username = st.session_state.get("username", "")
    assistants = load_assistants(username) if username else []
    
    # ===== METRICS CARDS =====
    st.markdown("<span style='color: var(--text-secondary); font-size: 0.85rem; font-weight: 600;'>YOUR STATS</span>", unsafe_allow_html=True)
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4, gap="medium")
    
    with metric_col1:
        st.metric(
            "Assistants",
            len(assistants),
            delta="Your AI team",
            delta_color="off",
            label_visibility="collapsed"
        )
    
    with metric_col2:
        ollama_connected = check_ollama_connection()
        st.metric(
            "Ollama",
            "🟢 Online" if ollama_connected else "🔴 Offline",
            delta="Local engine",
            delta_color="off",
            label_visibility="collapsed"
        )
    
    with metric_col3:
        available_backends = get_available_backends(
            bool(st.session_state.get("claude_key")),
            bool(st.session_state.get("grok_key")),
            bool(st.session_state.get("openai_key"))
        )
        st.metric(
            "Backends",
            len(available_backends),
            delta="Available",
            delta_color="off",
            label_visibility="collapsed"
        )
    
    with metric_col4:
        try:
            usage_count = len(open("usage.log").readlines()) if os.path.exists("usage.log") else 0
            st.metric(
                "Actions",
                usage_count,
                delta="Total used",
                delta_color="off",
                label_visibility="collapsed"
            )
        except:
            st.metric(
                "Actions",
                0,
                delta="Total used",
                delta_color="off",
                label_visibility="collapsed"
            )
    
    st.divider()
    
    # ===== TWO COLUMN LAYOUT =====
    col1, col2 = st.columns([2, 1], gap="medium")
    
    with col1:
        # Quick Test
        st.markdown("<h3 style='margin: 0 0 16px 0;'>⚡ Quick Test</h3>", unsafe_allow_html=True)
        
        backends = get_available_backends(
            bool(st.session_state.get("claude_key")),
            bool(st.session_state.get("grok_key")),
            bool(st.session_state.get("openai_key"))
        )
        
        if not backends:
            st.info("📌 No backends available. Configure API keys or set up Ollama in Settings.")
            return
        
        selected_backend = st.selectbox(
            "Select Backend",
            backends,
            key="home_backend_select",
            label_visibility="collapsed"
        )
        
        backend_key = backend_to_key(selected_backend)
        
        # Model selector (only for Ollama)
        if backend_key == "ollama":
            available_models = list_ollama_models()
            if not available_models:
                st.warning("⚠️ No Ollama models. Pull one: `ollama pull llama3`")
                return
            selected_model = st.selectbox("Select Model", available_models, key="home_model_select", label_visibility="collapsed")
        else:
            selected_model = None
        
        # Test prompt
        test_prompt = st.text_area(
            "Your prompt",
            placeholder="Ask me anything...",
            height=100,
            key="home_test_prompt",
            label_visibility="collapsed"
        )
        
        col_send, col_clear = st.columns(2)
        with col_send:
            test_button = st.button("🚀 Send", type="primary", use_container_width=True)
        with col_clear:
            if st.button("Clear", use_container_width=True):
                st.rerun()
        
        if test_button:
            if test_prompt.strip():
                st.markdown("<h4>Response</h4>", unsafe_allow_html=True)
                with st.spinner("⏳ Generating..."):
                    try:
                        messages = [{"role": "user", "content": test_prompt}]
                        api_key = None
                        
                        if backend_key == "claude":
                            api_key = st.session_state.get("claude_key")
                        elif backend_key == "chatgpt":
                            api_key = st.session_state.get("openai_key")
                        elif backend_key == "grok":
                            api_key = st.session_state.get("grok_key")
                        
                        response_placeholder = st.empty()
                        full_response = ""
                        
                        for chunk in generate_response(
                            messages,
                            backend=backend_key,
                            model=selected_model,
                            api_key=api_key
                        ):
                            full_response += chunk
                            response_placeholder.markdown(full_response)
                        
                        st.success("✅ Done!")
                        
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("Please enter a prompt.")
    
    with col2:
        # Recent Activity
        st.markdown("<h3 style='margin: 0 0 16px 0;'>📝 Recent</h3>", unsafe_allow_html=True)
        
        recent = get_recent_activity(username)
        if recent:
            for idx, asst in enumerate(recent):
                st.markdown(
                    f"""
                    <div class="card" style="padding: 12px; cursor: pointer;">
                        <div style="font-weight: 600; font-size: 0.9rem; color: var(--accent);">{asst.get('name', 'Untitled')}</div>
                        <div style="color: var(--text-secondary); font-size: 0.8rem; margin-top: 4px;">{asst.get('description', '')[:50]}...</div>
                        <div style="color: var(--text-secondary); font-size: 0.75rem; margin-top: 6px;">
                            {asst.get('created_at', 'N/A')[:10]}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No assistants yet. Create your first one!")
    
    st.divider()
    
    # ===== QUICK START TUTORIAL =====
    with st.expander("📚 Quick Start Guide", expanded=False):
        st.markdown("""
        #### Getting Started in 5 Minutes
        
        **Step 1: Create an Assistant**
        1. Go to **Create** page
        2. Enter a name (e.g., "Python Expert")
        3. Write a system prompt describing the assistant's behavior
        4. Optionally upload a knowledge base (PDF/TXT)
        5. Click Create
        
        **Step 2: Configure Backends**
        1. Open **Settings** → API Keys
        2. Add your API keys (Claude, ChatGPT, Grok) or set up Ollama
        3. Click test buttons to verify connections
        
        **Step 3: Chat with Your Assistant**
        1. Go to **Chat** page
        2. Select your assistant and preferred backend
        3. Start chatting!
        
        #### Local Setup (Ollama)
        ```bash
        # Install Ollama
        curl https://ollama.ai/install.sh | sh
        
        # Start the server
        ollama serve
        
        # Pull a model (in another terminal)
        ollama pull llama3
        ollama pull mistral
        ollama pull neural-chat
        ```
        
        #### Popular Models
        - **llama3** – Fast, versatile
        - **mistral** – Smart, efficient
        - **neural-chat** – Great for conversations
        - **codeup** – Code-specialized
        """)
    
    st.divider()
    
    # ===== CTA BUTTONS =====
    st.markdown("<span style='color: var(--text-secondary); font-size: 0.85rem; font-weight: 600;'>NEXT STEPS</span>", unsafe_allow_html=True)
    
    cta_col1, cta_col2, cta_col3 = st.columns(3, gap="medium")
    
    with cta_col1:
        if st.button("✨ Create Assistant", use_container_width=True):
            st.switch_page("pages:create_assistant.py")
    
    with cta_col2:
        if st.button("⚙️ Configure Settings", use_container_width=True):
            st.switch_page("pages:settings.py")
    
    with cta_col3:
        if st.button("💬 Open Chat", use_container_width=True):
            st.switch_page("pages:chat.py")


if __name__ == "__main__":
    render()
