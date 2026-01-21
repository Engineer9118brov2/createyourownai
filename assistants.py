"""My Assistants page - Premium grid layout with search and filters"""
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
    """Render premium my assistants page."""
    # Header
    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <h1 style="margin: 0 0 8px 0;">👥 My Assistants</h1>
            <p style="color: var(--text-secondary); margin: 0;">Manage and interact with your AI assistants</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    username = st.session_state.get("username", "")
    assistants = load_assistants(username)
    
    if not assistants:
        st.markdown(
            """
            <div style="text-align: center; padding: 60px 20px;">
                <h2 style="color: var(--text-secondary);">📭 No assistants yet</h2>
                <p style="color: var(--text-secondary);">Create your first AI assistant to get started</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("✨ Create Your First Assistant", use_container_width=True, type="primary"):
            st.switch_page("create_assistant.py")
        return
    
    # Search and filter bar
    st.markdown("<span style='color: var(--text-secondary); font-size: 0.85rem; font-weight: 600;'>SEARCH & FILTER</span>", unsafe_allow_html=True)
    
    search_col, filter_col = st.columns([2, 1], gap="medium")
    
    with search_col:
        search_term = st.text_input(
            "Search by name or description",
            placeholder="Search assistants...",
            label_visibility="collapsed"
        )
    
    with filter_col:
        show_status = st.selectbox(
            "Filter by status",
            ["All", "Active", "Draft"],
            label_visibility="collapsed"
        )
    
    # Filter assistants
    filtered_assistants = assistants
    
    if search_term:
        search_lower = search_term.lower()
        filtered_assistants = [
            a for a in filtered_assistants
            if search_lower in a.get("name", "").lower() or
               search_lower in a.get("description", "").lower()
        ]
    
    if show_status != "All":
        filtered_assistants = [a for a in filtered_assistants if a.get("status") == show_status]
    
    st.divider()
    
    # Display count
    st.markdown(
        f"<span style='color: var(--text-secondary); font-size: 0.85rem; font-weight: 600;'>SHOWING {len(filtered_assistants)} OF {len(assistants)}</span>",
        unsafe_allow_html=True
    )
    
    # Assistant cards grid
    if filtered_assistants:
        cols = st.columns(2, gap="medium")
        
        for idx, assistant in enumerate(filtered_assistants):
            with cols[idx % 2]:
                # Card container
                st.markdown(
                    f"""
                    <div class="card">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                            <div style="flex: 1;">
                                <div style="font-weight: 700; font-size: 1.1rem; color: var(--text-primary); margin-bottom: 6px;">
                                    {assistant['name']}
                                </div>
                                <div class="badge {'badge-accent' if assistant.get('status') == 'Active' else 'badge-danger'}">
                                    {assistant.get('status', 'Active')}
                                </div>
                            </div>
                        </div>
                        
                        <div style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5; margin-bottom: 12px;">
                            {assistant['description']}
                        </div>
                        
                        <div style="display: flex; gap: 12px; font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 16px;">
                            {'<span>📚 Knowledge Base</span>' if assistant.get('knowledge_base') else ''}
                            <span>📅 {assistant['created_at'][:10]}</span>
                        </div>
                        
                        <div style="border-top: 1px solid var(--border); padding-top: 12px;">
                            <div style="font-size: 0.8rem; color: var(--text-secondary);">
                                System: <code>{assistant['system_prompt'][:40]}...</code>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Action buttons
                col1, col2, col3 = st.columns(3, gap="small")
                
                with col1:
                    if st.button("💬 Chat", key=f"chat_{assistant['id']}", use_container_width=True):
                        st.session_state.current_assistant_id = assistant["id"]
                        st.switch_page("chat.py")
                
                with col2:
                    if st.button("📥 Export", key=f"export_{assistant['id']}", use_container_width=True):
                        assistant_json = json.dumps(assistant, indent=2)
                        st.download_button(
                            label="Download",
                            data=assistant_json,
                            file_name=f"{assistant['name'].replace(' ', '_').replace('/', '-')}.json",
                            mime="application/json",
                            key=f"download_{assistant['id']}",
                            use_container_width=True
                        )
                
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{assistant['id']}", use_container_width=True):
                        if st.session_state.get(f"confirm_delete_{assistant['id']}", False):
                            assistants = [a for a in assistants if a["id"] != assistant["id"]]
                            save_assistants(assistants, username)
                            st.success(f"✅ Deleted '{assistant['name']}'")
                            st.rerun()
                        else:
                            st.session_state[f"confirm_delete_{assistant['id']}"] = True
                            st.warning("Click again to confirm delete")
    else:
        st.info("No assistants match your search.")
    
    st.divider()
    
    # Import section
    st.markdown("<span style='color: var(--text-secondary); font-size: 0.85rem; font-weight: 600;'>IMPORT ASSISTANT</span>", unsafe_allow_html=True)
    st.markdown("Import a previously exported assistant JSON file")
    
    uploaded_json = st.file_uploader(
        "Choose a JSON file to import",
        type=["json"],
        key="import_json",
        label_visibility="collapsed"
    )
    
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
                
                st.markdown(
                    f"""
                    <div class="badge badge-accent">
                        ✅ Valid assistant file: <strong>{imported_assistant['name']}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                if st.button("✅ Confirm Import", type="primary", use_container_width=True):
                    assistants.append(imported_assistant)
                    save_assistants(assistants, username)
                    st.success(f"✅ Successfully imported '{imported_assistant['name']}'!")
                    st.rerun()
            else:
                st.error("❌ Invalid JSON format. Missing required fields: name, description, system_prompt")
        except json.JSONDecodeError:
            st.error("❌ Invalid JSON file. Please check the file format.")


if __name__ == "__main__":
    render()
