"""
No-Code AI Assistant Builder - Streamlit App (Enhanced)
Multi-backend AI assistant builder with local Ollama and cloud API support (Claude, ChatGPT, Grok).
Features: Assistant creation/management, knowledge base (RAG), export/import, usage analytics, and more.
"""

import streamlit as st
import json
import os
import uuid
import base64
from datetime import datetime
from pathlib import Path
from typing import Optional
import PyPDF2
import io

from ai_helper import (
    check_ollama_connection,
    list_ollama_models,
    generate_response,
    get_available_backends,
    backend_to_key
)

# Configuration
ASSISTANTS_FILE = "assistants.json"

# ========================
# THEME & STYLING
# ========================

def apply_theme(theme: str = "dark"):
    """Apply custom CSS theme."""
    if theme == "dark":
        st.markdown("""
        <style>
        :root {
            --primary-color: #00D9FF;
            --background-color: #0E1117;
            --secondary-background-color: #161B22;
            --text-color: #C9D1D9;
        }
        
        body {
            background-color: var(--background-color);
            color: var(--text-color);
        }
        
        .stButton > button {
            border-radius: 8px;
            padding: 10px 20px;
            background: linear-gradient(90deg, #00D9FF, #0084FF);
            color: white;
            font-weight: bold;
            border: none;
        }
        
        .stButton > button:hover {
            transform: scale(1.02);
            box-shadow: 0 0 20px rgba(0, 217, 255, 0.5);
        }
        </style>
        """, unsafe_allow_html=True)
    else:  # light theme
        st.markdown("""
        <style>
        :root {
            --primary-color: #0084FF;
            --background-color: #FFFFFF;
            --secondary-background-color: #F6F8FB;
            --text-color: #24292E;
        }
        
        body {
            background-color: var(--background-color);
            color: var(--text-color);
        }
        
        .stButton > button {
            border-radius: 8px;
            padding: 10px 20px;
            background: linear-gradient(90deg, #0084FF, #00D9FF);
            color: white;
            font-weight: bold;
            border: none;
        }
        
        .stButton > button:hover {
            transform: scale(1.02);
            box-shadow: 0 0 20px rgba(0, 132, 255, 0.3);
        }
        </style>
        """, unsafe_allow_html=True)


def get_assistants_file(username: Optional[str] = None) -> str:
    """Get the assistants file path for a user."""
    if username and username.strip():
        return f"{username.lower()}_assistants.json"
    return ASSISTANTS_FILE


def load_assistants(username: Optional[str] = None) -> list[dict]:
    """Load assistants from JSON file (per-user if username provided)."""
    file = get_assistants_file(username)
    if not os.path.exists(file):
        return []
    try:
        with open(file, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_assistants(assistants: list[dict], username: Optional[str] = None) -> None:
    """Save assistants to JSON file (per-user if username provided)."""
    file = get_assistants_file(username)
    with open(file, "w") as f:
        json.dump(assistants, f, indent=2)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"


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
    """Render the Home page with dashboard and quick test."""
    st.title("🏠 Home")
    
    # Welcome section
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        # Welcome to Your AI Assistant Builder
        
        Create and manage custom AI assistants powered by local and cloud models.
        """)
    with col2:
        if st.session_state.username:
            st.info(f"� **{st.session_state.username}**")
    
    st.divider()
    
    # Dashboard
    st.subheader("📊 Dashboard")
    
    username = st.session_state.get("username")
    assistants = load_assistants(username)
    
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
        1. **Create an Assistant**: Go to "Create Assistant" and fill in name, description, and system prompt
        2. **Configure API Keys**: Go to "Settings" to add cloud API keys (Claude, ChatGPT, Grok)
        3. **Test Your Assistant**: Go to "Test Chat" to chat with your assistant
        4. **Manage Assistants**: Go to "My Assistants" to edit, delete, or export assistants
        
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


def render_create_assistant_page():
    """Render the Create Assistant page with RAG support."""
    st.title("✨ Create Assistant")
    
    username = st.session_state.get("username")
    assistants = load_assistants(username)
    
    st.markdown("Create a new custom AI assistant with a personalized system prompt and optional knowledge base.")
    st.divider()
    
    # Form for creating assistant
    with st.form("create_assistant_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Assistant Name",
                placeholder="e.g., Python Expert, Writing Coach",
                max_chars=50
            )
        
        with col2:
            status = st.selectbox(
                "Status",
                ["Active", "Draft"],
                help="Active assistants appear in chat, drafts are hidden"
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
        
        # RAG - Knowledge base upload
        st.markdown("#### 📚 Knowledge Base (Optional)")
        st.caption("Upload a PDF or text file to give your assistant context")
        
        uploaded_file = st.file_uploader(
            "Upload knowledge base file",
            type=["txt", "pdf"],
            key="kb_upload"
        )
        
        knowledge_base = ""
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                knowledge_base = extract_text_from_pdf(uploaded_file.read())
            else:
                knowledge_base = uploaded_file.read().decode("utf-8")
            
            st.success(f"✅ Loaded {len(knowledge_base)} characters from file")
            with st.expander("Preview"):
                st.text(knowledge_base[:500] + "...")
        
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
                "knowledge_base": knowledge_base[:5000] if knowledge_base else "",  # Store first 5000 chars
                "status": status,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            assistants.append(new_assistant)
            save_assistants(assistants, username)
            
            st.success(f"✅ Assistant '{name}' created successfully!")
            st.balloons()
            
            # Log the action
            from pages.settings import log_usage
            log_usage("assistant_created", f"name={name}, has_kb={bool(knowledge_base)}")
    
    # Display current assistants
    if assistants:
        st.divider()
        st.subheader(f"📋 Your Assistants ({len(assistants)})")
        
        for assistant in assistants:
            with st.expander(f"� {assistant['name']} · {assistant['status']}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Description:** {assistant['description']}")
                    st.markdown(f"**System Prompt:** `{assistant['system_prompt'][:100]}...`")
                    if assistant.get('knowledge_base'):
                        st.markdown(f"**Knowledge Base:** {len(assistant['knowledge_base'])} chars")
                    st.caption(f"Created: {assistant['created_at']}")
                
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_create_{assistant['id']}"):
                        assistants = [a for a in assistants if a["id"] != assistant["id"]]
                        save_assistants(assistants, username)
                        st.success("Deleted!")
                        st.rerun()


def render_my_assistants_page():
    """Render the My Assistants page with export/import."""
    st.title("👥 My Assistants")
    
    username = st.session_state.get("username")
    assistants = load_assistants(username)
    
    if not assistants:
        st.info("📭 No assistants created yet. Go to 'Create Assistant' to get started!")
        return
    
    # Filter by status
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"**{len(assistants)}** assistant(s) available")
    with col2:
        show_drafts = st.checkbox("Show Drafts")
    with col3:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    st.divider()
    
    # Display assistants
    for assistant in assistants:
        if assistant.get("status") == "Draft" and not show_drafts:
            continue
        
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.subheader(f"📦 {assistant['name']}")
                st.markdown(f"_{assistant['description']}_")
                
                if assistant.get('knowledge_base'):
                    st.caption(f"📚 Knowledge Base: {len(assistant['knowledge_base'])} chars")
                
                st.caption(f"Status: {assistant.get('status', 'Active')} | Created: {assistant['created_at'][:10]}")
            
            with col2:
                if st.button("💬 Chat", key=f"chat_{assistant['id']}", use_container_width=True):
                    st.session_state.current_assistant_id = assistant["id"]
                    st.switch_page("pages/chat.py")
            
            with col3:
                with st.popover("⋮", use_container_width=True):
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        if st.button("📥 Export", key=f"export_{assistant['id']}", use_container_width=True):
                            assistant_json = json.dumps(assistant, indent=2)
                            st.download_button(
                                label="Download JSON",
                                data=assistant_json,
                                file_name=f"{assistant['name'].replace(' ', '_')}.json",
                                mime="application/json",
                                key=f"download_{assistant['id']}"
                            )
                    
                    with col_b:
                        if st.button("✏️ Edit", key=f"edit_{assistant['id']}", use_container_width=True):
                            st.info("Edit feature coming soon!")
                    
                    with col_c:
                        if st.button("🗑️ Delete", key=f"delete_{assistant['id']}", use_container_width=True):
                            assistants = [a for a in assistants if a["id"] != assistant["id"]]
                            save_assistants(assistants, username)
                            st.success(f"Deleted '{assistant['name']}'")
                            st.rerun()
            
            st.divider()
    
    # Import section
    st.subheader("📤 Import Assistant")
    st.markdown("Import a previously exported assistant JSON file")
    
    uploaded_json = st.file_uploader("Choose JSON file", type=["json"], key="import_json")
    if uploaded_json:
        try:
            imported_assistant = json.load(uploaded_json)
            
            # Validate
            required_fields = ["name", "description", "system_prompt"]
            if all(field in imported_assistant for field in required_fields):
                # Add new fields if missing
                if "id" not in imported_assistant:
                    imported_assistant["id"] = str(uuid.uuid4())
                if "created_at" not in imported_assistant:
                    imported_assistant["created_at"] = datetime.now().isoformat()
                if "status" not in imported_assistant:
                    imported_assistant["status"] = "Active"
                
                if st.button("✅ Confirm Import", type="primary"):
                    assistants.append(imported_assistant)
                    save_assistants(assistants, username)
                    st.success(f"✅ Imported '{imported_assistant['name']}'!")
                    st.rerun()
            else:
                st.error("Invalid JSON format. Missing required fields.")
        except json.JSONDecodeError:
            st.error("Invalid JSON file.")


def render_test_chat_page():
    """Render the Test Chat page with multi-backend support."""
    st.title("💬 Test Chat")
    
    username = st.session_state.get("username")
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
                    from pages.settings import log_usage
                    log_usage("chat_message", f"backend={backend_key}, assistant={current_assistant['name'] if current_assistant else 'none'}")
                
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
        if st.button("� Export Chat", use_container_width=True):
            chat_json = json.dumps(st.session_state.chat_history, indent=2)
            st.download_button(
                label="Download Chat",
                data=chat_json,
                file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("🏠 Back to Home", use_container_width=True):
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
    
    # Apply theme
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"
    apply_theme(st.session_state.theme)
    
    # Sidebar header
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        st.sidebar.title("🤖 Builder")
    with col2:
        if st.sidebar.button("⚙️", key="settings_header", help="Go to Settings"):
            st.switch_page("pages/settings.py")
    
    # Sidebar navigation
    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Home", "✨ Create", "👥 Assistants", "💬 Chat"],
        label_visibility="collapsed"
    )
    
    st.sidebar.divider()
    
    # User info
    if st.session_state.username:
        st.sidebar.markdown(f"**👤 {st.session_state.username}**")
    
    # Backend status
    st.sidebar.markdown("### 🔌 Backends")
    backends = get_available_backends(
        bool(st.session_state.get("claude_key")),
        bool(st.session_state.get("grok_key")),
        bool(st.session_state.get("openai_key"))
    )
    
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
    
    # About section
    st.sidebar.markdown("""
    ### ℹ️ About
    No-code AI assistant builder with local & cloud models.
    
    **v1.1.0** | [GitHub](https://github.com)
    """)
    
    # Render selected page
    page_map = {
        "🏠 Home": render_home_page,
        "✨ Create": render_create_assistant_page,
        "👥 Assistants": render_my_assistants_page,
        "💬 Chat": render_test_chat_page
    }
    
    if page in page_map:
        page_map[page]()
    else:
        st.error("Page not found")


if __name__ == "__main__":
    main()
