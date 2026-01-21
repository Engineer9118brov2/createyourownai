"""Home page - Dashboard and quick test"""
import streamlit as st
import os
from ai_helper import (
    check_ollama_connection,
    list_ollama_models,
    generate_response,
    get_available_backends,
    backend_to_key
)

def render():
    """Render home page."""
    st.title("Welcome to Your AI Assistant Builder")
    
    st.markdown("""
    Create and manage custom AI assistants powered by local and cloud models.
    """)
    
    st.divider()
    
    # Dashboard
    st.subheader("📊 Dashboard")
    
    username = st.session_state.get("username", "")
    assistants = load_assistants(username) if username else []
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    with metric_col1:
        st.metric("Assistants Created", len(assistants))
    with metric_col2:
        ollama_connected = check_ollama_connection()
        st.metric("Ollama Status", "🟢 Online" if ollama_connected else "🔴 Offline")
    with metric_col3:
        available_backends = get_available_backends(
            bool(st.session_state.get("claude_key")),
            bool(st.session_state.get("grok_key")),
            bool(st.session_state.get("openai_key"))
        )
        st.metric("Backends Available", len(available_backends))
    with metric_col4:
        try:
            usage_count = len(open("usage.log").readlines()) if os.path.exists("usage.log") else 0
            st.metric("Total Actions", usage_count)
        except:
            st.metric("Total Actions", 0)
    
    st.divider()
    
    # Quick start tutorial
    with st.expander("📚 Quick Start Tutorial", expanded=False):
        st.markdown("""
        1. **Create an Assistant**: Go to "Create" and fill in name, description, and system prompt
        2. **Configure API Keys**: Go to "Settings" to add cloud API keys (Claude, ChatGPT, Grok)
        3. **Test Your Assistant**: Go to "Chat" to chat with your assistant
        4. **Manage Assistants**: Go to "Assistants" to edit, delete, or export assistants
        
        **Need help with Ollama?**
        - Install: `curl https://ollama.ai/install.sh | sh`
        - Run: `ollama serve`
        - Pull model: `ollama pull llama3`
        """)
    
    st.divider()
    
    # Quick test section
    st.subheader("⚡ Quick Test")
    
    # Backend selector
    backends = get_available_backends(
        bool(st.session_state.get("claude_key")),
        bool(st.session_state.get("grok_key")),
        bool(st.session_state.get("openai_key"))
    )
    
    selected_backend = st.selectbox(
        "Select Backend",
        backends,
        key="home_backend_select"
    )
    
    backend_key = backend_to_key(selected_backend)
    
    # Model selector (only for Ollama)
    if backend_key == "ollama":
        available_models = list_ollama_models()
        if not available_models:
            st.warning("⚠️ No Ollama models available. Pull one using: `ollama pull llama3`")
            return
        selected_model = st.selectbox("Select Model", available_models, key="home_model_select")
    else:
        selected_model = None
    
    # Test prompt
    test_prompt = st.text_area(
        "Enter a test prompt:",
        placeholder="Ask me anything...",
        height=100,
        key="home_test_prompt"
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        test_button = st.button("Send Test Prompt", type="primary", use_container_width=True)
    with col2:
        st.write("")  # spacing
        if st.button("Clear", use_container_width=True):
            st.rerun()
    
    if test_button:
        if test_prompt.strip():
            st.subheader("Response:")
            with st.spinner("⏳ Generating response..."):
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


def load_assistants(username: str = ""):
    """Load assistants from JSON file (per-user if username provided)."""
    import json
    file = f"{username.lower()}_assistants.json" if username else "assistants.json"
    if not os.path.exists(file):
        return []
    try:
        with open(file, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


if __name__ == "__main__":
    render()
