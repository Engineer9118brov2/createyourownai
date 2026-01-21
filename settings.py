"""Settings page - Premium configuration with modern tab layout"""
import streamlit as st
import os
import json
from datetime import datetime
from ai_helper import (
    check_ollama_connection,
    list_ollama_models,
    delete_ollama_model,
    pull_ollama_model
)

def log_usage(action: str, details: str = ""):
    """Log usage analytics to file."""
    try:
        log_file = "usage.log"
        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp} | {action} | {details}\n"
        
        with open(log_file, "a") as f:
            f.write(log_entry)
    except Exception:
        pass

def render():
    """Render premium settings page."""
    # Header
    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <h1 style="margin: 0 0 8px 0;">⚙️ Settings & Configuration</h1>
            <p style="color: var(--text-secondary); margin: 0;">Manage your account, API keys, models, and deployment</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.divider()
    
    # Create tabs for organization
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["👤 Profile", "🔑 API Keys", "🦙 Models", "🎨 Theme", "🚀 Deploy", "📊 Analytics"]
    )
    
    # Tab 1: Profile
    with tab1:
        st.markdown("##### 👤 User Profile")
        
        username = st.text_input(
            "Username",
            value=st.session_state.get("username", ""),
            placeholder="Your name or username",
            max_chars=50,
            label_visibility="collapsed"
        )
        
        if username != st.session_state.get("username", ""):
            st.session_state.username = username
            log_usage("profile_update", f"username set to {username}")
            st.success(f"✅ Username updated to '{username}'")
        
        st.caption("📌 Your assistants are stored per-user in separate files")
        st.divider()
        
        st.markdown("##### 📂 Data & Storage")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Profile", "Per-User Storage", delta="username-based", delta_color="off")
        
        with col2:
            if username:
                file_path = f"{username.lower()}_assistants.json"
                st.metric("Storage File", f"{file_path}", delta_color="off")
            else:
                st.metric("Storage File", "assistants.json (default)", delta_color="off")
    
    # Tab 2: API Keys
    with tab2:
        st.markdown("##### 🔑 Cloud API Keys")
        
        st.markdown(
            """
            <div class="badge badge-danger" style="margin-bottom: 16px;">
                ⚠️ Security: Keys stored in session only, never saved to disk. Close your browser to clear.
            </div>
            """,
            unsafe_allow_html=True
        )
        
        col1, col2, col3 = st.columns(3, gap="medium")
        
        with col1:
            st.markdown("<strong>🤖 Claude (Anthropic)</strong>", unsafe_allow_html=True)
            claude_key = st.text_input(
                "Claude API Key",
                value=st.session_state.get("claude_key", ""),
                type="password",
                placeholder="sk-ant-...",
                key="claude_input",
                label_visibility="collapsed"
            )
            if claude_key != st.session_state.get("claude_key", ""):
                st.session_state.claude_key = claude_key
                log_usage("api_key_update", "claude_key configured")
            
            if st.button("🧪 Test", key="test_claude", use_container_width=True):
                if claude_key:
                    st.success("✅ Claude configured")
                else:
                    st.warning("⚠️ No key provided")
            
            if st.session_state.get("claude_key"):
                st.markdown("<div class='badge badge-success'>✅ Configured</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='badge badge-danger'>❌ Not Configured</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<strong>💬 ChatGPT (OpenAI)</strong>", unsafe_allow_html=True)
            openai_key = st.text_input(
                "OpenAI API Key",
                value=st.session_state.get("openai_key", ""),
                type="password",
                placeholder="sk-...",
                key="openai_input",
                label_visibility="collapsed"
            )
            if openai_key != st.session_state.get("openai_key", ""):
                st.session_state.openai_key = openai_key
                log_usage("api_key_update", "openai_key configured")
            
            if st.button("🧪 Test", key="test_openai", use_container_width=True):
                if openai_key:
                    st.success("✅ ChatGPT configured")
                else:
                    st.warning("⚠️ No key provided")
            
            if st.session_state.get("openai_key"):
                st.markdown("<div class='badge badge-success'>✅ Configured</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='badge badge-danger'>❌ Not Configured</div>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("<strong>⚡ Grok (xAI)</strong>", unsafe_allow_html=True)
            grok_key = st.text_input(
                "Grok API Key",
                value=st.session_state.get("grok_key", ""),
                type="password",
                placeholder="xai-...",
                key="grok_input",
                label_visibility="collapsed"
            )
            if grok_key != st.session_state.get("grok_key", ""):
                st.session_state.grok_key = grok_key
                log_usage("api_key_update", "grok_key configured")
            
            if st.button("🧪 Test", key="test_grok", use_container_width=True):
                if grok_key:
                    st.success("✅ Grok configured")
                else:
                    st.warning("⚠️ No key provided")
            
            if st.session_state.get("grok_key"):
                st.markdown("<div class='badge badge-success'>✅ Configured</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='badge badge-danger'>❌ Not Configured</div>", unsafe_allow_html=True)
        
        st.divider()
        st.markdown("##### 📚 Getting API Keys")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            **Claude API**
            1. Visit [console.anthropic.com](https://console.anthropic.com)
            2. Sign up/Login
            3. Go to API keys
            4. Create new key
            5. Copy & paste here
            """)
        
        with col2:
            st.markdown("""
            **OpenAI API**
            1. Visit [platform.openai.com](https://platform.openai.com)
            2. Sign up/Login  
            3. Go to API keys
            4. Create new key
            5. Copy & paste here
            """)
        
        with col3:
            st.markdown("""
            **Grok API**
            1. Visit [console.x.ai](https://console.x.ai)
            2. Sign up/Login
            3. Create API key
            4. Copy & paste here
            5. Ready to use!
            """)
    
    # Tab 3: Models
    with tab3:
        st.markdown("##### 🦙 Ollama Model Management")
        
        if not check_ollama_connection():
            st.error("⚠️ Ollama is not running. Cannot manage models.")
            st.markdown("""
            **To start Ollama:**
            ```bash
            ollama serve
            ```
            """)
        else:
            st.markdown(
                "<div class='badge badge-success'>✅ Ollama Connected</div>",
                unsafe_allow_html=True
            )
            
            col1, col2 = st.columns(2, gap="medium")
            
            with col1:
                st.markdown("**Pull New Model**")
                model_to_pull = st.selectbox(
                    "Popular Models",
                    [
                        "llama3",
                        "mistral",
                        "neural-chat",
                        "zephyr",
                        "openchat",
                        "phi",
                        "orca-mini",
                        "custom (enter below)"
                    ],
                    key="model_pull_select",
                    label_visibility="collapsed"
                )
                
                if model_to_pull == "custom (enter below)":
                    custom_model = st.text_input("Enter model name", placeholder="e.g., gpt4all")
                    model_to_pull = custom_model if custom_model else "llama3"
                
                if st.button("📥 Pull Model", use_container_width=True, type="primary"):
                    st.info(f"📥 Pulling {model_to_pull}... This may take a few minutes.")
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    try:
                        for i, status in enumerate(pull_ollama_model(model_to_pull)):
                            status_text.text(status)
                            progress_bar.progress(min((i + 1) / 10, 1.0))
                        
                        st.success(f"✅ {model_to_pull} pulled successfully!")
                        log_usage("model_pull", model_to_pull)
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            with col2:
                st.markdown("**Available Models**")
                available_models = list_ollama_models()
                
                if available_models:
                    st.markdown(f"**{len(available_models)} model(s) available:**")
                    for model in available_models:
                        col_name, col_delete = st.columns([4, 1])
                        with col_name:
                            st.markdown(f"<div class='badge badge-accent'>📦 {model}</div>", unsafe_allow_html=True)
                        with col_delete:
                            if st.button("🗑️", key=f"delete_{model}", help="Delete model"):
                                try:
                                    delete_ollama_model(model)
                                    st.success(f"✅ Deleted {model}")
                                    log_usage("model_delete", model)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                else:
                    st.info("📭 No models available. Pull a model to get started.")
    
    # Tab 4: Theme
    with tab4:
        st.markdown("##### 🎨 Appearance & Theme")
        
        theme = st.radio(
            "Select Theme",
            ["Dark", "Light"],
            index=0 if st.session_state.get("theme", "dark") == "dark" else 1,
            horizontal=True,
            label_visibility="collapsed"
        )
        
        new_theme = "dark" if theme == "Dark" else "light"
        if new_theme != st.session_state.get("theme", "dark"):
            st.session_state.theme = new_theme
            log_usage("theme_change", f"changed to {new_theme}")
            st.info(f"🎭 Theme changed to {theme}. Refresh page to see changes.")
        
        st.divider()
        
        st.markdown("##### 🎯 UI Customization")
        st.markdown("""
        The app features:
        - **Dark Mode** (default): Easy on the eyes, modern aesthetic
        - **Light Mode**: Classic, professional look
        - **Card-based layouts**: Clean, organized interface
        - **Responsive design**: Works on desktop and mobile
        - **Smooth interactions**: Hover effects, transitions
        """)

    
    # Tab 5: Deployment
    with tab5:
        st.markdown("##### 🚀 Deployment Guides")
        
        st.markdown("Deploy your AI Assistant Builder to the cloud in minutes.")
        
        deployment_option = st.selectbox(
            "Choose Deployment Platform",
            ["Docker", "Streamlit Cloud", "Heroku", "AWS EC2"],
            label_visibility="collapsed"
        )
        
        if deployment_option == "Docker":
            st.markdown("""
            #### 🐳 Docker Deployment
            
            Create a `Dockerfile`:
            
            ```dockerfile
            FROM python:3.12-slim
            WORKDIR /app
            COPY requirements.txt .
            RUN pip install --no-cache-dir -r requirements.txt
            COPY . .
            EXPOSE 8501
            CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
            ```
            
            **Build and run:**
            ```bash
            docker build -t ai-assistant-builder .
            docker run -p 8501:8501 ai-assistant-builder
            ```
            """)
        
        elif deployment_option == "Streamlit Cloud":
            st.markdown("""
            #### ☁️ Streamlit Cloud Deployment
            
            **Steps:**
            1. Push code to GitHub
            2. Visit [share.streamlit.io](https://share.streamlit.io)
            3. Click "New app" → Select repo, branch, main file
            4. Click "Deploy"
            
            **Add secrets (Settings → Secrets):**
            ```
            CLAUDE_KEY=your-key
            OPENAI_KEY=your-key
            GROK_KEY=your-key
            OLLAMA_HOST=http://localhost:11434
            ```
            """)
        
        elif deployment_option == "Heroku":
            st.markdown("""
            #### 🔴 Heroku Deployment
            
            **Create `Procfile`:**
            ```
            web: streamlit run app.py --logger.level=error
            ```
            
            **Create `runtime.txt`:**
            ```
            python-3.12.1
            ```
            
            **Deploy:**
            ```bash
            heroku create your-app-name
            heroku config:set CLAUDE_KEY=your-key
            git push heroku main
            ```
            """)
        
        elif deployment_option == "AWS EC2":
            st.markdown("""
            #### 🟠 AWS EC2 Deployment
            
            1. **Launch** EC2 instance (Ubuntu 24.04)
            2. **SSH** into instance
            3. **Clone repo:**
               ```bash
               git clone https://github.com/you/createyourownai.git
               cd createyourownai
               ```
            4. **Install:**
               ```bash
               pip install -r requirements.txt
               ```
            5. **Run:**
               ```bash
               nohup streamlit run app.py --server.port 8501 &
               ```
            6. **Access:** `http://your-ec2-ip:8501`
            """)

    
    # Tab 6: Analytics
    with tab6:
        st.markdown("##### 📊 Usage Analytics")
        
        log_file = "usage.log"
        
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                lines = f.readlines()
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Actions", len(lines), delta_color="off")
            with col2:
                st.metric("Log File", "usage.log", delta_color="off")
            with col3:
                st.metric("Status", "✅ Active", delta_color="off")
            
            st.divider()
            
            # Count action types
            action_counts = {}
            for line in lines:
                if " | " in line:
                    parts = line.split(" | ")
                    if len(parts) >= 2:
                        action = parts[1].strip()
                        action_counts[action] = action_counts.get(action, 0) + 1
            
            if action_counts:
                st.markdown("**Action Breakdown:**")
                
                cols = st.columns(len(action_counts))
                for idx, (action, count) in enumerate(sorted(action_counts.items(), key=lambda x: x[1], reverse=True)):
                    with cols[idx % len(cols)]:
                        st.metric(action.replace("_", " ").title(), count, delta_color="off")
            
            st.divider()
            
            with st.expander("📋 View Logs (Last 50 entries)"):
                st.code("".join(lines[-50:]), language="text")
        else:
            st.info("📭 No usage logs yet. Actions will be tracked here.")
        
        if st.button("🗑️ Clear Logs", use_container_width=True):
            if os.path.exists(log_file):
                os.remove(log_file)
            st.success("✅ Logs cleared")
            st.rerun()
    
    st.divider()
    
    # Session management
    st.markdown("##### 🔐 Session Management")
    
    col1, col2, col3 = st.columns(3, gap="medium")
    
    with col1:
        if st.button("🔑 Clear API Keys", use_container_width=True):
            st.session_state.claude_key = ""
            st.session_state.openai_key = ""
            st.session_state.grok_key = ""
            st.success("✅ API keys cleared from session")
            log_usage("session_action", "api_keys_cleared")
    
    with col2:
        if st.button("🔄 Reset All Settings", use_container_width=True):
            st.session_state.username = ""
            st.session_state.claude_key = ""
            st.session_state.openai_key = ""
            st.session_state.grok_key = ""
            st.session_state.theme = "dark"
            st.success("✅ All settings reset to defaults")
            log_usage("session_action", "all_settings_cleared")
    
    with col3:
        if st.button("🔄 Refresh Page", use_container_width=True):
            st.rerun()


if __name__ == "__main__":
    render()
