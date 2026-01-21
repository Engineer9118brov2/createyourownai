"""My Assistants page"""
import streamlit as st
import json
import os
import uuid
from datetime import datetime


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


def render():
    """Render my assistants page."""
    st.title("👥 My Assistants")
    
    username = st.session_state.get("username", "")
    assistants = load_assistants(username)
    
    if not assistants:
        st.info("📭 No assistants created yet. Go to 'Create' to get started!")
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
                    st.switch_page("chat.py")
            
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


if __name__ == "__main__":
    render()
