"""
No-Code AI Assistant Builder - Streamlit App
Allows users to create, manage, and chat with custom AI assistants using Ollama.
"""

import streamlit as st
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from ollama_helper import check_connection, list_models, generate_response

# Configuration
ASSISTANTS_FILE = "assistants.json"


def load_assistants() -> list[dict]:
    """Load assistants from JSON file."""
    if not os.path.exists(ASSISTANTS_FILE):
        return []
    try:
        with open(ASSISTANTS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_assistants(assistants: list[dict]) -> None:
    """Save assistants to JSON file."""
    with open(ASSISTANTS_FILE, "w") as f:
        json.dump(assistants, f, indent=2)


def get_assistant_by_id(assistants: list[dict], assistant_id: str) -> Optional[dict]:
    """Get assistant by ID."""
    for assistant in assistants:
        if assistant.get("id") == assistant_id:
            return assistant
    return None


def init_session_state():
    """Initialize session state variables."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "current_assistant_id" not in st.session_state:
        st.session_state.current_assistant_id = None
    if "current_model" not in st.session_state:
        st.session_state.current_model = None


def render_home_page():
    """Render the Home page."""
    st.title("🏠 Home")
    
    # Welcome message
    st.markdown("""
    # Welcome to Your AI Assistant Builder
    
    Build and manage custom AI assistants powered by local open models via Ollama.
    
    **Features:**
    - ✨ Create custom assistants with personalized system prompts
    - 💬 Chat with your assistants using local models
    - 📊 Manage multiple assistants
    - 🔒 100% local - your data stays on your machine
    """)
    
    st.divider()
    
    # Ollama connection status
    st.subheader("Connection Status")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        is_connected = check_connection()
        status_icon = "🟢" if is_connected else "🔴"
        status_text = "Connected" if is_connected else "Disconnected"
        st.metric("Ollama Status", status_text, delta=status_icon)
    
    if not is_connected:
        st.warning(
            "⚠️ Could not connect to Ollama. Please ensure Ollama is running at "
            "http://localhost:11434 (or configured in .env)"
        )
        st.markdown(
            "**To get started:**\n"
            "1. Install Ollama from [ollama.ai](https://ollama.ai)\n"
            "2. Run `ollama serve` in a terminal\n"
            "3. Pull a model: `ollama pull llama3`"
        )
        return
    
    # Model selection and quick test
    st.subheader("Quick Test")
    
    available_models = list_models()
    if not available_models:
        st.error("No models available. Please pull a model using `ollama pull llama3`")
        return
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_model = st.selectbox(
            "Select Model",
            available_models,
            key="home_model_select"
        )
    
    with col2:
        st.write("")  # spacing
        if st.button("Refresh Models", use_container_width=True):
            st.rerun()
    
    # Quick test prompt
    test_prompt = st.text_area(
        "Enter a test prompt:",
        placeholder="Ask me anything...",
        height=100
    )
    
    if st.button("Send Test Prompt", type="primary"):
        if test_prompt.strip():
            st.subheader("Response:")
            with st.spinner("Generating response..."):
                try:
                    messages = [{"role": "user", "content": test_prompt}]
                    response_placeholder = st.empty()
                    full_response = ""
                    
                    for chunk in generate_response(messages, model=selected_model):
                        full_response += chunk
                        response_placeholder.markdown(full_response)
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a prompt.")


def render_create_assistant_page():
    """Render the Create Assistant page."""
    st.title("✨ Create Assistant")
    
    assistants = load_assistants()
    
    st.markdown("Create a new custom AI assistant with a personalized system prompt.")
    st.divider()
    
    # Form for creating assistant
    with st.form("create_assistant_form"):
        name = st.text_input(
            "Assistant Name",
            placeholder="e.g., Python Expert, Writing Coach",
            max_chars=50
        )
        
        description = st.text_area(
            "Description",
            placeholder="Brief description of what this assistant does",
            height=60,
            max_chars=200
        )
        
        system_prompt = st.text_area(
            "System Prompt",
            value="You are a helpful assistant.",
            height=120,
            max_chars=2000,
            help="This defines the assistant's behavior and personality"
        )
        
        submitted = st.form_submit_button("Create Assistant", type="primary", use_container_width=True)
    
    if submitted:
        if not name.strip():
            st.error("Please enter an assistant name.")
        elif not description.strip():
            st.error("Please enter a description.")
        elif not system_prompt.strip():
            st.error("Please enter a system prompt.")
        else:
            # Create new assistant
            new_assistant = {
                "id": str(uuid.uuid4()),
                "name": name.strip(),
                "description": description.strip(),
                "system_prompt": system_prompt.strip(),
                "created_at": datetime.now().isoformat()
            }
            
            assistants.append(new_assistant)
            save_assistants(assistants)
            
            st.success(f"✅ Assistant '{name}' created successfully!")
            st.balloons()
    
    # Display current assistants
    if assistants:
        st.divider()
        st.subheader(f"Current Assistants ({len(assistants)})")
        
        for assistant in assistants:
            with st.expander(f"📋 {assistant['name']}"):
                st.markdown(f"**Description:** {assistant['description']}")
                st.markdown(f"**System Prompt:** `{assistant['system_prompt']}`")
                st.caption(f"Created: {assistant['created_at']}")


def render_my_assistants_page():
    """Render the My Assistants page."""
    st.title("👥 My Assistants")
    
    assistants = load_assistants()
    
    if not assistants:
        st.info("No assistants created yet. Go to 'Create Assistant' to get started!")
        return
    
    st.markdown(f"You have **{len(assistants)}** assistant(s).")
    st.divider()
    
    for assistant in assistants:
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.subheader(f"📦 {assistant['name']}")
                st.markdown(f"_{assistant['description']}_")
                st.caption(f"System Prompt: {assistant['system_prompt'][:60]}...")
            
            with col2:
                if st.button("💬 Chat", key=f"chat_{assistant['id']}", use_container_width=True):
                    st.session_state.current_assistant_id = assistant["id"]
                    st.switch_page("pages/test_chat.py" if os.path.exists("pages/test_chat.py") else None)
                    st.rerun()
            
            with col3:
                if st.button("✏️ Edit", key=f"edit_{assistant['id']}", use_container_width=True):
                    st.info("Edit functionality coming soon!")
            
            with col4:
                if st.button("🗑️ Delete", key=f"delete_{assistant['id']}", use_container_width=True):
                    # Remove assistant
                    assistants = [a for a in assistants if a["id"] != assistant["id"]]
                    save_assistants(assistants)
                    st.success(f"Deleted '{assistant['name']}'")
                    st.rerun()
            
            st.divider()


def render_test_chat_page():
    """Render the Test Chat page."""
    st.title("💬 Test Chat")
    
    assistants = load_assistants()
    is_connected = check_connection()
    available_models = list_models() if is_connected else []
    
    if not is_connected:
        st.error("⚠️ Ollama is not running. Please start it and try again.")
        return
    
    if not available_models:
        st.error("No models available. Please pull a model using `ollama pull llama3`")
        return
    
    # Sidebar for assistant and model selection
    st.sidebar.markdown("### Settings")
    
    assistant_names = {a["id"]: a["name"] for a in assistants}
    assistant_options = ["Default (No Assistant)"] + list(assistant_names.values())
    
    selected_assistant_name = st.sidebar.selectbox(
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
    
    selected_model = st.sidebar.selectbox(
        "Select Model",
        available_models,
        key="chat_model_select"
    )
    
    # Display system prompt
    if current_assistant:
        st.sidebar.markdown("### System Prompt")
        st.sidebar.markdown(f"```\n{current_assistant['system_prompt']}\n```")
    
    st.divider()
    
    # Chat interface
    st.subheader("Conversation")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
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
            
            with st.spinner("Generating response..."):
                try:
                    system_prompt = current_assistant["system_prompt"] if current_assistant else None
                    
                    # Prepare messages for API
                    messages = []
                    for msg in st.session_state.chat_history:
                        if msg["role"] in ["user", "assistant"]:
                            messages.append({
                                "role": msg["role"],
                                "content": msg["content"]
                            })
                    
                    # Stream response
                    for chunk in generate_response(
                        messages,
                        model=selected_model,
                        system_prompt=system_prompt
                    ):
                        full_response += chunk
                        response_placeholder.markdown(full_response)
                    
                    # Add assistant message to history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": full_response
                    })
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # Clear chat button
    if st.session_state.chat_history:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_history = []
                st.rerun()
        with col2:
            if st.button("🏠 Back to Home"):
                st.switch_page("pages/home.py")


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="AI Assistant Builder",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Sidebar navigation
    st.sidebar.title("🤖 AI Assistant Builder")
    
    page = st.sidebar.radio(
        "Navigation",
        ["Home", "Create Assistant", "My Assistants", "Test Chat"],
        label_visibility="collapsed"
    )
    
    st.sidebar.divider()
    
    # About section
    st.sidebar.markdown("""
    ### About
    A no-code AI assistant builder using local models via Ollama.
    
    [Ollama](https://ollama.ai) • [Streamlit](https://streamlit.io)
    """)
    
    # Render selected page
    if page == "Home":
        render_home_page()
    elif page == "Create Assistant":
        render_create_assistant_page()
    elif page == "My Assistants":
        render_my_assistants_page()
    elif page == "Test Chat":
        render_test_chat_page()


if __name__ == "__main__":
    main()
