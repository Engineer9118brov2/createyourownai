"""Chat page"""
import streamlit as st
import json
import os
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


def render():
    """Render chat page."""
    st.title("💬 Test Chat")
    
    username = st.session_state.get("username", "")
    assistants = load_assistants(username)
    
    # Sidebar settings
    with st.sidebar:
        st.markdown("### ⚙️ Chat Settings")
        
        # Assistant selector
        assistant_names = {a["id"]: a["name"] for a in assistants if a.get("status") != "Draft"}
        assistant_options = ["Default (No Assistant)"] + list(assistant_names.values())
        
        selected_assistant_name = st.selectbox(
            "Select Assistant",
            assistant_options,
            key="chat_assistant_select"
        )
        
        # Get selected assistant
        current_assistant = None
        if selected_assistant_name != "Default (No Assistant)":
            for a in assistants:
                if a["name"] == selected_assistant_name:
                    current_assistant = a
                    break
        
        # Backend selector
        backends = get_available_backends(
            bool(st.session_state.get("claude_key")),
            bool(st.session_state.get("grok_key")),
            bool(st.session_state.get("openai_key"))
        )
        
        selected_backend = st.selectbox(
            "Select Backend",
            backends,
            key="chat_backend_select"
        )
        
        backend_key = backend_to_key(selected_backend)
        
        # Model selector
        if backend_key == "ollama":
            available_models = list_ollama_models()
            if available_models:
                selected_model = st.selectbox(
                    "Select Model",
                    available_models,
                    key="chat_model_select"
                )
            else:
                st.warning("No Ollama models available")
                selected_model = None
        else:
            selected_model = None
        
        # Display system prompt
        if current_assistant:
            st.markdown("### 📝 System Prompt")
            st.info(current_assistant['system_prompt'])
            
            if current_assistant.get('knowledge_base'):
                with st.expander("📚 Knowledge Base"):
                    st.text(current_assistant['knowledge_base'][:500])
    
    # Check connection
    if backend_key == "ollama" and not check_ollama_connection():
        st.error("⚠️ Ollama is not running. Please start it first.")
        return
    
    if backend_key == "ollama" and not list_ollama_models():
        st.error("No Ollama models available. Pull one: `ollama pull llama3`")
        return
    
    st.divider()
    
    # Chat header
    chat_title = f"💬 Chat with {current_assistant['name']}" if current_assistant else "💬 Chat"
    st.markdown(f"## {chat_title}")
    
    # Display chat history
    for i, message in enumerate(st.session_state.chat_history):
        with st.chat_message(message["role"]):
            col1, col2 = st.columns([20, 1])
            
            with col1:
                st.markdown(message["content"])
            
            with col2:
                if st.button("📋", key=f"copy_{i}", help="Copy message"):
                    st.info("Copied to clipboard!")
    
    # User input
    if user_input := st.chat_input("Type your message..."):
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            with st.spinner("⏳ Generating..."):
                try:
                    # Build system prompt with knowledge base
                    system_prompt = None
                    if current_assistant:
                        system_prompt = current_assistant["system_prompt"]
                        if current_assistant.get('knowledge_base'):
                            system_prompt += f"\n\n**Knowledge Base Context:**\n{current_assistant['knowledge_base']}"
                    
                    # Prepare messages for API
                    messages = []
                    for msg in st.session_state.chat_history:
                        if msg["role"] in ["user", "assistant"]:
                            messages.append({
                                "role": msg["role"],
                                "content": msg["content"]
                            })
                    
                    # Get API key if needed
                    api_key = None
                    if backend_key == "claude":
                        api_key = st.session_state.get("claude_key")
                    elif backend_key == "chatgpt":
                        api_key = st.session_state.get("openai_key")
                    elif backend_key == "grok":
                        api_key = st.session_state.get("grok_key")
                    
                    # Stream response
                    for chunk in generate_response(
                        messages,
                        backend=backend_key,
                        model=selected_model,
                        system_prompt=system_prompt,
                        api_key=api_key
                    ):
                        full_response += chunk
                        response_placeholder.markdown(full_response)
                    
                    # Add assistant message to history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": full_response
                    })
                    
                    # Log the action
                    try:
                        with open("usage.log", "a") as f:
                            f.write(f"{datetime.now().isoformat()} | chat_message | backend={backend_key}, assistant={current_assistant['name'] if current_assistant else 'none'}\n")
                    except:
                        pass
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    st.divider()
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    with col2:
        if st.button("💾 Export Chat", use_container_width=True):
            chat_json = json.dumps(st.session_state.chat_history, indent=2)
            st.download_button(
                label="Download Chat",
                data=chat_json,
                file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.switch_page("home.py")


if __name__ == "__main__":
    render()
