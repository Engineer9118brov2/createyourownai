"""
Settings page for AI Assistant Builder.
Handles API keys, user profile, theme, model management, and deployment helpers.
"""

import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path

from ai_helper import (
    check_ollama_connection, 
    list_ollama_models, 
    delete_ollama_model,
    pull_ollama_model
)


def init_settings_state():
    """Initialize settings in session state."""
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"
    if "claude_key" not in st.session_state:
        st.session_state.claude_key = ""
    if "openai_key" not in st.session_state:
        st.session_state.openai_key = ""
    if "grok_key" not in st.session_state:
        st.session_state.grok_key = ""


def log_usage(action: str, details: str = ""):
    """Log usage analytics to file."""
    try:
        log_file = "usage.log"
        timestamp = datetime.now().isoformat()
        log_entry = f"{timestamp} | {action} | {details}\n"
        
        with open(log_file, "a") as f:
            f.write(log_entry)
    except Exception:
        pass  # Silently fail if logging not possible


def render_profile_section():
    """Render user profile settings."""
    st.subheader("👤 User Profile")
    
    username = st.text_input(
        "Username",
        value=st.session_state.username,
        placeholder="Your name or username",
        max_chars=50
    )
    
    if username != st.session_state.username:
        st.session_state.username = username
        log_usage("profile_update", f"username set to {username}")
        st.success(f"✅ Username updated to '{username}'")
    
    st.caption("Your assistants are stored per-user in separate files.")


def render_theme_section():
    """Render theme settings."""
    st.subheader("🎨 Theme")
    
    theme = st.radio(
        "Select Theme",
        ["Dark", "Light"],
        index=0 if st.session_state.theme == "dark" else 1,
        horizontal=True
    )
    
    new_theme = "dark" if theme == "Dark" else "light"
    if new_theme != st.session_state.theme:
        st.session_state.theme = new_theme
        log_usage("theme_change", f"changed to {new_theme}")
        st.info(f"🎭 Theme changed to {theme}. Refresh page to see changes.")


def render_api_keys_section():
    """Render cloud API key settings."""
    st.subheader("🔑 Cloud API Keys")
    
    st.markdown("Store API keys securely in session (never saved to disk).")
    st.warning(
        "⚠️ **Security:** API keys are stored only in your current session. "
        "They are never saved to files or logs. Close your browser to clear them."
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### Claude (Anthropic)")
        claude_key = st.text_input(
            "Claude API Key",
            value=st.session_state.claude_key,
            type="password",
            placeholder="sk-ant-...",
            key="claude_input"
        )
        if claude_key != st.session_state.claude_key:
            st.session_state.claude_key = claude_key
            log_usage("api_key_update", "claude_key configured")
        
        if st.session_state.claude_key:
            st.success("✅ Claude configured")
        else:
            st.caption("Not configured")
    
    with col2:
        st.markdown("#### ChatGPT (OpenAI)")
        openai_key = st.text_input(
            "OpenAI API Key",
            value=st.session_state.openai_key,
            type="password",
            placeholder="sk-...",
            key="openai_input"
        )
        if openai_key != st.session_state.openai_key:
            st.session_state.openai_key = openai_key
            log_usage("api_key_update", "openai_key configured")
        
        if st.session_state.openai_key:
            st.success("✅ ChatGPT configured")
        else:
            st.caption("Not configured")
    
    with col3:
        st.markdown("#### Grok (xAI)")
        grok_key = st.text_input(
            "Grok API Key",
            value=st.session_state.grok_key,
            type="password",
            placeholder="xai-...",
            key="grok_input"
        )
        if grok_key != st.session_state.grok_key:
            st.session_state.grok_key = grok_key
            log_usage("api_key_update", "grok_key configured")
        
        if st.session_state.grok_key:
            st.success("✅ Grok configured")
        else:
            st.caption("Not configured")


def render_ollama_models_section():
    """Render Ollama model management."""
    st.subheader("🦙 Ollama Model Management")
    
    if not check_ollama_connection():
        st.error("⚠️ Ollama is not running. Cannot manage models.")
        return
    
    st.markdown("Pull, view, or delete models from your local Ollama instance.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Pull New Model")
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
            key="model_pull_select"
        )
        
        if model_to_pull == "custom (enter below)":
            custom_model = st.text_input("Enter model name", placeholder="e.g., gpt4all")
            model_to_pull = custom_model if custom_model else "llama3"
        
        if st.button("Pull Model", use_container_width=True):
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
        st.markdown("#### Available Models")
        available_models = list_ollama_models()
        
        if available_models:
            st.write(f"**{len(available_models)} model(s) available:**")
            for model in available_models:
                col_name, col_delete = st.columns([4, 1])
                with col_name:
                    st.caption(f"📦 {model}")
                with col_delete:
                    if st.button("🗑️", key=f"delete_{model}", help="Delete model"):
                        try:
                            delete_ollama_model(model)
                            st.success(f"Deleted {model}")
                            log_usage("model_delete", model)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        else:
            st.info("No models available. Pull a model to get started.")


def render_deployment_section():
    """Render deployment helper."""
    st.subheader("🚀 Deployment Helper")
    
    st.markdown("Quick guides and code snippets for deploying your app.")
    
    deployment_option = st.selectbox(
        "Choose Deployment Target",
        ["Docker", "Streamlit Cloud", "Heroku", "AWS EC2", "Vercel"]
    )
    
    if deployment_option == "Docker":
        st.markdown("#### Docker Deployment")
        docker_content = """
Create a `Dockerfile` in your project root:

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
"""
        st.markdown(docker_content)
        
        if st.button("📋 Copy Dockerfile Content"):
            st.info("Dockerfile content copied to clipboard")
    
    elif deployment_option == "Streamlit Cloud":
        st.markdown("#### Streamlit Cloud Deployment")
        streamlit_content = """
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repository, branch, and main file (app.py)
5. Click "Deploy"

**Add secrets in Streamlit Cloud dashboard:**
- Go to App Settings → Secrets
- Add your API keys:
  ```
  CLAUDE_KEY=your-key
  OPENAI_KEY=your-key
  GROK_KEY=your-key
  OLLAMA_HOST=http://localhost:11434
  ```
"""
        st.markdown(streamlit_content)
    
    elif deployment_option == "Heroku":
        st.markdown("#### Heroku Deployment")
        heroku_content = """
1. Create `Procfile`:
   ```
   web: streamlit run app.py --logger.level=error
   ```

2. Create `runtime.txt`:
   ```
   python-3.12.1
   ```

3. Deploy:
   ```bash
   heroku create your-app-name
   heroku config:set CLAUDE_KEY=your-key
   git push heroku main
   ```
"""
        st.markdown(heroku_content)
    
    elif deployment_option == "AWS EC2":
        st.markdown("#### AWS EC2 Deployment")
        aws_content = """
1. Launch EC2 instance (Ubuntu 24.04)
2. SSH into instance
3. Clone your repo:
   ```bash
   git clone https://github.com/you/createyourownai.git
   cd createyourownai
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run with nohup:
   ```bash
   nohup streamlit run app.py --server.port 8501 &
   ```
6. Access via `http://your-ec2-ip:8501`
"""
        st.markdown(aws_content)
    
    elif deployment_option == "Vercel":
        st.markdown("#### Vercel Deployment (Advanced)")
        vercel_content = """
Streamlit is not ideal for Vercel (serverless), but you can:

1. Use [Streamlit + FastAPI wrapper](https://docs.streamlit.io/deployment/tutorials/deploy-streamlit-using-aws-ec2)
2. Or containerize with Docker and deploy to:
   - AWS ECS
   - Google Cloud Run
   - Azure Container Instances

Recommended: Use Docker + AWS EC2 or Cloud Run for best compatibility.
"""
        st.markdown(vercel_content)


def render_analytics_section():
    """Render usage analytics."""
    st.subheader("📊 Usage Analytics")
    
    log_file = "usage.log"
    
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            lines = f.readlines()
        
        st.metric("Total Actions", len(lines))
        
        # Count action types
        action_counts = {}
        for line in lines:
            if " | " in line:
                parts = line.split(" | ")
                if len(parts) >= 2:
                    action = parts[1].strip()
                    action_counts[action] = action_counts.get(action, 0) + 1
        
        if action_counts:
            st.write("**Actions breakdown:**")
            for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True):
                st.caption(f"• {action}: {count}")
        
        with st.expander("📋 View Raw Logs"):
            st.code("".join(lines[-50:]), language="text")  # Last 50 entries
    else:
        st.info("No usage logs yet. Actions will be tracked here.")
    
    if st.button("🗑️ Clear Logs"):
        if os.path.exists(log_file):
            os.remove(log_file)
        st.success("Logs cleared")
        st.rerun()


def render_session_management():
    """Render session management."""
    st.subheader("🔐 Session Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Clear API Keys", use_container_width=True):
            st.session_state.claude_key = ""
            st.session_state.openai_key = ""
            st.session_state.grok_key = ""
            st.success("✅ API keys cleared from session")
            log_usage("session_action", "api_keys_cleared")
    
    with col2:
        if st.button("Clear All Settings", use_container_width=True):
            st.session_state.username = ""
            st.session_state.claude_key = ""
            st.session_state.openai_key = ""
            st.session_state.grok_key = ""
            st.session_state.theme = "dark"
            st.success("✅ All settings cleared")
            log_usage("session_action", "all_settings_cleared")
    
    with col3:
        if st.button("Refresh", use_container_width=True):
            st.rerun()


def render_settings_page():
    """Main settings page."""
    st.title("⚙️ Settings")
    st.markdown("Configure your AI Assistant Builder, API keys, models, and more.")
    st.divider()
    
    init_settings_state()
    
    # Create tabs for organization
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["👤 Profile", "🎨 Theme", "🔑 API Keys", "🦙 Models", "🚀 Deploy", "📊 Analytics"]
    )
    
    with tab1:
        render_profile_section()
    
    with tab2:
        render_theme_section()
    
    with tab3:
        render_api_keys_section()
    
    with tab4:
        render_ollama_models_section()
    
    with tab5:
        render_deployment_section()
    
    with tab6:
        render_analytics_section()
    
    st.divider()
    
    render_session_management()
    
    st.divider()
    
    st.markdown("""
    ### About This App
    **AI Assistant Builder** | v1.1.0
    
    Built with ❤️ using:
    - Streamlit for UI
    - Ollama for local AI
    - Anthropic, OpenAI, xAI for cloud APIs
    
    [GitHub](https://github.com/Engineer9118brov2/createyourownai)
    """)
