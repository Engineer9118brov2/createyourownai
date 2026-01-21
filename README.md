# 🤖 AI Assistant Builder

A no-code AI assistant builder prototype with **local Ollama support** and **cloud API integration** (Claude, ChatGPT, Grok). Built with Streamlit for a simple, intuitive interface.

## ✨ Features

- **🏠 Home Dashboard**: Connection status, available backends, usage analytics, quick test
- **✨ Create Assistants**: Multi-field form with system prompts and knowledge base (RAG)
- **👥 Manage Assistants**: Create, edit, delete, export/import assistants as JSON
- **💬 Multi-Backend Chat**: Switch between Ollama (local), Claude, ChatGPT, or Grok
- **📚 Knowledge Base (RAG)**: Upload PDF/TXT files to give assistants context
- **🎨 Theme Support**: Dark/Light mode toggle
- **👤 User Profiles**: Per-user assistant storage
- **🔑 API Key Management**: Secure session-based storage for API keys
- **📊 Usage Analytics**: Track actions and usage patterns
- **🚀 Deployment Helpers**: Docker, Streamlit Cloud, Heroku, AWS EC2 snippets
- **⚙️ Model Management**: Pull, list, delete Ollama models from UI

## 🛠️ Tech Stack

- **Frontend**: Streamlit 1.28+
- **Local AI**: Ollama
- **Cloud APIs**: Anthropic Claude, OpenAI ChatGPT, xAI Grok
- **Data**: JSON files (per-user), PyPDF2 for document extraction
- **Python**: 3.10+

## 📦 Quick Installation

```bash
# Clone and setup
git clone https://github.com/Engineer9118brov2/createyourownai.git
cd createyourownai
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Setup environment (optional)
cp .env.template .env

# Install Ollama (optional, for local models)
# macOS: brew install ollama
# Linux: curl https://ollama.ai/install.sh | sh
# Windows: Download from https://ollama.ai

# Start Ollama (in separate terminal)
ollama serve

# Pull a model
ollama pull llama3

# Run the app
streamlit run app.py
```

Access at `http://localhost:8501`

## 🚀 Quick Start

1. **Settings** ⚙️ → Set username, add API keys (optional)
2. **Create Assistant** ✨ → Name, description, system prompt
3. **Test Chat** 💬 → Select assistant & backend, chat!
4. **My Assistants** 👥 → Export, import, manage assistants

## 📄 Files

- `app.py` - Main Streamlit app with all pages
- `ai_helper.py` - Unified backend interface (Ollama, Claude, ChatGPT, Grok)
- `pages/settings.py` - Settings, API keys, model management, analytics
- `assistants.json` - Default (empty) assistants file
- `requirements.txt` - Python dependencies
- `.env.template` - Environment variables template

## 🔑 API Keys (Optional)

All API keys are stored in-memory (session state only) - never written to disk!

- **Claude**: [console.anthropic.com](https://console.anthropic.com)
- **ChatGPT**: [platform.openai.com](https://platform.openai.com)
- **Grok**: [console.x.ai](https://console.x.ai)

## 🐳 Docker

```bash
docker build -t ai-assistant-builder .
docker run -p 8501:8501 ai-assistant-builder
```

## 📊 Troubleshooting

**Ollama not connecting?**
```bash
curl http://localhost:11434/api/tags
ollama serve
```

**No models?**
```bash
ollama pull llama3
```

**API key issues?**
- Verify key is correct in Settings
- Check service credentials are active
- Clear session and re-enter

## 📝 Features in Detail

### Home
- Dashboard with connection status
- Quick test any backend
- Quick-start tutorial

### Create Assistant
- Name, description, system prompt
- Optional knowledge base (PDF/TXT)
- Status (Active/Draft)

### My Assistants
- View all assistants
- Export as JSON
- Import from JSON
- Delete assistants

### Test Chat
- Select assistant & backend
- Full message history
- Copy message button
- Export chat as JSON

### Settings
- User profile & theme
- API key management
- Ollama model management
- Deployment guides
- Usage analytics
- Session management

## 📄 License

MIT License

---

**Need help?** Check the [Streamlit docs](https://docs.streamlit.io) or open an issue!
