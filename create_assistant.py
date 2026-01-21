"""Create Assistant page - Premium form with templates and RAG support"""
import streamlit as st
import json
import os
import uuid
from datetime import datetime
import PyPDF2
import io

# Prompt templates for quick creation
PROMPT_TEMPLATES = {
    "Helpful Assistant": "You are a helpful, harmless, and honest AI assistant. Provide clear, accurate, and thoughtful responses.",
    "Code Reviewer": "You are an expert code reviewer. Analyze code for bugs, suggest improvements, and explain best practices.",
    "Writing Coach": "You are a professional writing coach. Help improve clarity, tone, grammar, and overall quality of written content.",
    "Data Analyst": "You are a data analytics expert. Help interpret data, create visualizations, and provide insights from datasets.",
    "Creative Writer": "You are a creative writer and storyteller. Help users develop stories, characters, dialogues, and creative content.",
    "Python Expert": "You are a Python expert. Help with code, explain concepts, debug issues, and suggest optimizations.",
    "Product Manager": "You are an experienced product manager. Help with strategy, roadmaps, user research, and feature prioritization.",
    "Customer Support": "You are a friendly customer support agent. Help resolve issues, answer questions, and maintain positive relationships.",
}

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

def save_assistants(assistants: list, username: str = ""):
    """Save assistants to JSON file (per-user if username provided)."""
    file = f"{username.lower()}_assistants.json" if username else "assistants.json"
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

def render():
    """Render premium create assistant page."""
    # Header
    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <h1 style="margin: 0 0 8px 0;">✨ Create Assistant</h1>
            <p style="color: var(--text-secondary); margin: 0;">Build a powerful AI assistant tailored to your needs</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    username = st.session_state.get("username", "")
    assistants = load_assistants(username)
    
    # Template selector
    st.markdown("<span style='color: var(--text-secondary); font-size: 0.85rem; font-weight: 600;'>QUICK START</span>", unsafe_allow_html=True)
    
    template_col1, template_col2 = st.columns([3, 1])
    
    with template_col1:
        selected_template = st.selectbox(
            "Use a template",
            ["Custom"] + list(PROMPT_TEMPLATES.keys()),
            label_visibility="collapsed",
            key="template_select"
        )
    
    with template_col2:
        if selected_template != "Custom":
            st.caption("Auto-fills system prompt →")
    
    st.divider()
    
    # Main form
    st.markdown("<span style='color: var(--text-secondary); font-size: 0.85rem; font-weight: 600;'>ASSISTANT DETAILS</span>", unsafe_allow_html=True)
    
    with st.form("create_assistant_form", border=False):
        # Basic info
        col1, col2 = st.columns(2, gap="medium")
        
        with col1:
            name = st.text_input(
                "Assistant Name",
                placeholder="e.g., Python Expert, Writing Coach",
                max_chars=50,
                label_visibility="collapsed"
            )
            st.caption("Clear, memorable name")
        
        with col2:
            status = st.selectbox(
                "Status",
                ["Active", "Draft"],
                label_visibility="collapsed"
            )
            st.caption("Active assistants appear in chat")
        
        # Description
        description = st.text_area(
            "Description",
            placeholder="What does this assistant do? e.g., 'Helps with Python code and debugging'",
            height=60,
            max_chars=200,
            label_visibility="collapsed"
        )
        st.caption("Brief overview (max 200 characters)")
        
        # System prompt with template support
        st.markdown("<span style='color: var(--text-secondary); font-size: 0.85rem; font-weight: 600; margin-top: 16px;'>SYSTEM PROMPT</span>", unsafe_allow_html=True)
        
        default_prompt = PROMPT_TEMPLATES.get(selected_template, "You are a helpful assistant.") if selected_template != "Custom" else "You are a helpful assistant."
        
        system_prompt = st.text_area(
            "System Prompt",
            value=default_prompt,
            height=120,
            max_chars=2000,
            label_visibility="collapsed",
            help="Defines the assistant's behavior, personality, and role"
        )
        st.caption("Instructions that guide the assistant's responses")
        
        # Knowledge base upload
        st.markdown("<span style='color: var(--text-secondary); font-size: 0.85rem; font-weight: 600; margin-top: 16px;'>KNOWLEDGE BASE (Optional)</span>", unsafe_allow_html=True)
        
        knowledge_base = ""
        uploaded_file = st.file_uploader(
            "Drag & drop or click to upload",
            type=["txt", "pdf"],
            key="kb_upload",
            label_visibility="collapsed"
        )
        
        kb_status = st.empty()
        
        if uploaded_file:
            try:
                if uploaded_file.type == "application/pdf":
                    knowledge_base = extract_text_from_pdf(uploaded_file.read())
                else:
                    knowledge_base = uploaded_file.read().decode("utf-8")
                
                char_count = len(knowledge_base)
                word_count = len(knowledge_base.split())
                
                kb_status.markdown(
                    f"""
                    <div class="badge badge-success">
                        ✅ File loaded: {char_count:,} characters, {word_count:,} words
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                with st.expander("📄 Preview"):
                    st.text(knowledge_base[:500] + "..." if len(knowledge_base) > 500 else knowledge_base)
            except Exception as e:
                kb_status.error(f"❌ Error loading file: {str(e)}")
                knowledge_base = ""
        
        st.divider()
        
        # Submit button
        col_submit, col_info = st.columns([1, 2])
        
        with col_submit:
            submitted = st.form_submit_button(
                "🚀 Create Assistant",
                type="primary",
                use_container_width=True
            )
        
        with col_info:
            st.caption(f"Total assistants: {len(assistants)}")
    
    # Handle form submission
    if submitted:
        errors = []
        
        if not name.strip():
            errors.append("Please enter an assistant name.")
        elif len(name.strip()) < 2:
            errors.append("Assistant name must be at least 2 characters.")
        
        if not description.strip():
            errors.append("Please enter a description.")
        
        if not system_prompt.strip():
            errors.append("Please enter a system prompt.")
        
        if errors:
            for error in errors:
                st.error(error)
        else:
            # Create new assistant
            new_assistant = {
                "id": str(uuid.uuid4()),
                "name": name.strip(),
                "description": description.strip(),
                "system_prompt": system_prompt.strip(),
                "knowledge_base": knowledge_base[:5000] if knowledge_base else "",
                "status": status,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            assistants.append(new_assistant)
            save_assistants(assistants, username)
            
            # Log the action
            try:
                with open("usage.log", "a") as f:
                    f.write(f"{datetime.now().isoformat()} | assistant_created | name={name}, has_kb={bool(knowledge_base)}\n")
            except:
                pass
            
            # Success feedback
            st.balloons()
            st.success(f"✅ Assistant '{name}' created successfully!")
            st.info("💡 Go to Chat page to start using your assistant, or create another one.")
            
            # Auto-redirect option
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💬 Go to Chat", use_container_width=True):
                    st.switch_page("chat.py")
            with col2:
                if st.button("📋 View All", use_container_width=True):
                    st.switch_page("assistants.py")
            with col3:
                if st.button("✨ Create Another", use_container_width=True):
                    st.rerun()
    
    st.divider()
    
    # Display current assistants as cards
    if assistants:
        st.markdown(f"<span style='color: var(--text-secondary); font-size: 0.85rem; font-weight: 600;'>YOUR ASSISTANTS ({len(assistants)})</span>", unsafe_allow_html=True)
        
        # Grid layout
        cols = st.columns(2, gap="medium")
        
        for idx, assistant in enumerate(assistants):
            with cols[idx % 2]:
                st.markdown(
                    f"""
                    <div class="card">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                            <div>
                                <div style="font-weight: 600; font-size: 1rem; color: var(--text-primary);">{assistant['name']}</div>
                                <div class="badge badge-accent" style="margin-top: 6px;">{assistant['status']}</div>
                            </div>
                        </div>
                        <div style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 12px;">{assistant['description']}</div>
                        <div style="color: var(--text-secondary); font-size: 0.8rem; margin-bottom: 12px;">
                            📅 {assistant['created_at'][:10]}
                            {' • 📚 +KB' if assistant.get('knowledge_base') else ''}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Action buttons
                col_edit, col_delete = st.columns(2)
                with col_edit:
                    if st.button("💬 Chat", key=f"chat_{assistant['id']}", use_container_width=True):
                        st.session_state.current_assistant_id = assistant['id']
                        st.switch_page("chat.py")
                
                with col_delete:
                    if st.button("🗑️ Delete", key=f"delete_create_{assistant['id']}", use_container_width=True):
                        assistants = [a for a in assistants if a["id"] != assistant["id"]]
                        save_assistants(assistants, username)
                        st.success("Deleted!")
                        st.rerun()


if __name__ == "__main__":
    render()
