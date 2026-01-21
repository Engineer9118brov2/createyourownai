"""Create Assistant page"""
import streamlit as st
import json
import os
import uuid
from datetime import datetime
import PyPDF2
import io


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
    """Render create assistant page."""
    st.title("✨ Create Assistant")
    
    username = st.session_state.get("username", "")
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
                "knowledge_base": knowledge_base[:5000] if knowledge_base else "",
                "status": status,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            assistants.append(new_assistant)
            save_assistants(assistants, username)
            
            st.success(f"✅ Assistant '{name}' created successfully!")
            st.balloons()
            
            # Log the action
            try:
                with open("usage.log", "a") as f:
                    f.write(f"{datetime.now().isoformat()} | assistant_created | name={name}, has_kb={bool(knowledge_base)}\n")
            except:
                pass
    
    # Display current assistants
    if assistants:
        st.divider()
        st.subheader(f"📋 Your Assistants ({len(assistants)})")
        
        for assistant in assistants:
            with st.expander(f"📦 {assistant['name']} · {assistant['status']}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Description:** {assistant['description']}")
                    st.markdown(f"**System Prompt:** `{assistant['system_prompt'][:100]}...`")
                    if assistant.get('knowledge_base'):
                        st.markdown(f"**Knowledge Base:** {len(assistant['knowledge_base'])} chars")
                    st.caption(f"Created: {assistant['created_at']}")
                
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_create_{assistant['id']}", use_container_width=True):
                        assistants = [a for a in assistants if a["id"] != assistant["id"]]
                        save_assistants(assistants, username)
                        st.success("Deleted!")
                        st.rerun()


if __name__ == "__main__":
    render()
