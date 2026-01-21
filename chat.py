"""Chat page - Modern multi-backend chat interface with streaming"""
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
    """Render premium chat page with modern UI."""
    username = st.session_state.get("username", "")
    assistants = load_assistants(username)
    
    # Sidebar settings
    with st.sidebar:
        st.markdown(
            """
            <div style="margin-bottom: 16px;">
                <span style="color: var(--text-secondary); font-size: 0.85rem; font-weight: 600;">CHAT SETTINGS</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Assistant selector
        assistant_names = {a["id"]: a["name"] for a in assistants if a.get("status") != "Draft"}
        assistant_options = ["Default (No Assistant)"] + list(assistant_names.values())
        
        selected_assistant_name = st.selectbox(
            "Select Assistant",
            assistant_options,
            key="chat_assistant_select",
            label_visibility="collapsed"
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
            key="chat_backend_select",
            label_visibility="collapsed"
        )
        
        backend_key = backend_to_key(selected_backend)
        
        # Model selector
        if backend_key == "ollama":
            available_models = list_ollama_models()
            if available_models:
                selected_model = st.selectbox(
                    "Select Model",
                    available_models,
                    key="chat_model_select",
                    label_visibility="collapsed"
                )
            else:
                st.warning("⚠️ No Ollama models available")
                selected_model = None
        else:
            selected_model = None
        
        st.divider()
        
        # Display system prompt and KB
        if current_assistant:
            st.markdown("<span style='color: var(--text-secondary); font-size: 0.85rem; font-weight: 600;'>SYSTEM PROMPT</span>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="badge badge-accent" style="word-wrap: break-word; padding: 12px;">
                    {current_assistant['system_prompt']}
                </div>
                """,
                unsafe_allow_html=True
            )
            
            if current_assistant.get('knowledge_base'):
                with st.expander("📚 Knowledge Base", expanded=False):
                    st.text(current_assistant['knowledge_base'][:300] + "..." if len(current_assistant['knowledge_base']) > 300 else current_assistant['knowledge_base'])
    
    # Check connection
    if backend_key == "ollama" and not check_ollama_connection():
        st.error("⚠️ Ollama is not running. Please start the Ollama service first.")
        st.markdown("```bash\nollama serve\n```")
        return
    
    if backend_key == "ollama" and not list_ollama_models():
        st.error("⚠️ No Ollama models available. Pull one: `ollama pull llama3`")
        return
    
    # Main chat area
    st.markdown(
        f"""
        <div style="margin-bottom: 24px;">
            <h1 style="margin: 0 0 8px 0;">💬 {'Chat with ' + current_assistant['name'] if current_assistant else 'Chat'}</h1>
            <p style="color: var(--text-secondary); margin: 0; font-size: 0.9rem;">{selected_backend}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.divider()
    
    # Chat message container with scrollable area
    st.markdown("<div id='chat-container' style='max-height: 600px; overflow-y: auto;'>", unsafe_allow_html=True)
    
    # Display chat history with modern styling
    for i, message in enumerate(st.session_state.chat_history):
        is_user = message["role"] == "user"
        alignment = "flex-end" if is_user else "flex-start"
        bg_color = "var(--accent)" if is_user else "var(--bg-secondary)"
        text_color = "white" if is_user else "var(--text-primary)"
        border_radius = "12px 12px 0 12px" if is_user else "12px 12px 12px 0"
        
        st.markdown(
            f"""
            <div style="display: flex; justify-content: {alignment}; margin-bottom: 16px;">
                <div style="max-width: 75%; background: {bg_color}; color: {text_color}; padding: 12px 16px; border-radius: {border_radius}; border: 1px solid var(--border);">
                    <div style="white-space: pre-wrap; word-wrap: break-word; font-size: 0.95rem;">
                        {message['content']}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # User input
    if user_input := st.chat_input("Type your message...", key="chat_input"):
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Display user message immediately
        st.rerun()
    
    # Generate response if last message is from user
    if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
        # Show typing indicator
        with st.spinner("✍️ Generating response..."):
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
                full_response = ""
                response_placeholder = st.empty()
                
                for chunk in generate_response(
                    messages,
                    backend=backend_key,
                    model=selected_model,
                    system_prompt=system_prompt,
                    api_key=api_key
                ):
                    full_response += chunk
                    with response_placeholder.container():
                        st.markdown(
                            f"""
                            <div style="display: flex; justify-content: flex-start; margin-bottom: 16px;">
                                <div style="max-width: 75%; background: var(--bg-secondary); color: var(--text-primary); padding: 12px 16px; border-radius: 12px 12px 12px 0; border: 1px solid var(--border);">
                                    <div style="white-space: pre-wrap; word-wrap: break-word; font-size: 0.95rem;">
                                        {full_response}
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                
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
                
                st.rerun()
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    st.divider()
    
    # Action buttons
    col1, col2, col3, col4 = st.columns(4, gap="small")
    
    with col1:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    with col2:
        if st.button("💾 Export", use_container_width=True):
            chat_json = json.dumps(st.session_state.chat_history, indent=2)
            st.download_button(
                label="📥 Download",
                data=chat_json,
                file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
                key="export_chat"
            )
    
    with col3:
        if st.button("🔄 New Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    with col4:
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("home.py")
    

if __name__ == "__main__":
    render()
