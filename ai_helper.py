"""
Unified AI helper for multiple backends: Ollama (local), Claude (Anthropic), ChatGPT (OpenAI), and Grok (xAI).
Routes requests based on selected backend and API key availability.
"""

import os
from typing import Generator, Optional
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3")


# ========================
# OLLAMA (Local)
# ========================

def check_ollama_connection() -> bool:
    """Check if Ollama server is running."""
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        return response.status_code == 200
    except (requests.RequestException, Exception):
        return False


def list_ollama_models() -> list[str]:
    """Fetch list of available Ollama models."""
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            model_names = []
            for model in models:
                if isinstance(model, dict) and "name" in model:
                    model_names.append(model["name"])
                elif isinstance(model, str):
                    model_names.append(model)
            return sorted(model_names) if model_names else []
        return []
    except (requests.RequestException, Exception):
        return []


def stream_ollama_response(
    messages: list[dict],
    model: str = DEFAULT_MODEL,
    system_prompt: Optional[str] = None
) -> Generator[str, None, None]:
    """Stream response from Ollama."""
    try:
        if system_prompt:
            has_system = any(msg.get("role") == "system" for msg in messages)
            if not has_system:
                messages = [{"role": "system", "content": system_prompt}] + messages
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
        }
        
        response = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json=payload,
            timeout=120,
            stream=True
        )
        
        if response.status_code != 200:
            yield f"Error: Ollama returned status code {response.status_code}"
            return
        
        for line in response.iter_lines():
            if line:
                try:
                    import json
                    chunk = json.loads(line)
                    if "message" in chunk and "content" in chunk["message"]:
                        yield chunk["message"]["content"]
                except (json.JSONDecodeError, KeyError):
                    continue
    
    except requests.exceptions.Timeout:
        yield "Error: Request to Ollama timed out."
    except requests.exceptions.ConnectionError:
        yield f"Error: Could not connect to Ollama at {OLLAMA_HOST}."
    except Exception as e:
        yield f"Error: {str(e)}"


def pull_ollama_model(model: str) -> Generator[str, None, None]:
    """Pull a model from Ollama registry."""
    try:
        payload = {"name": model}
        response = requests.post(
            f"{OLLAMA_HOST}/api/pull",
            json=payload,
            timeout=600,
            stream=True
        )
        
        if response.status_code != 200:
            yield f"Error: Could not pull model {model}"
            return
        
        for line in response.iter_lines():
            if line:
                try:
                    import json
                    chunk = json.loads(line)
                    if "status" in chunk:
                        yield chunk["status"]
                except (json.JSONDecodeError, KeyError):
                    continue
    
    except Exception as e:
        yield f"Error: {str(e)}"


def delete_ollama_model(model: str) -> bool:
    """Delete a model from Ollama."""
    try:
        response = requests.delete(
            f"{OLLAMA_HOST}/api/delete",
            json={"name": model},
            timeout=30
        )
        return response.status_code == 200
    except Exception:
        return False


# ========================
# CLAUDE (Anthropic)
# ========================

def stream_claude_response(
    messages: list[dict],
    api_key: str,
    system_prompt: Optional[str] = None,
    model: str = "claude-3-5-sonnet-20241022"
) -> Generator[str, None, None]:
    """Stream response from Claude via Anthropic API."""
    try:
        from anthropic import Anthropic
        
        client = Anthropic(api_key=api_key)
        
        # Build system message
        system_content = system_prompt or "You are a helpful assistant."
        
        # Convert messages format if needed
        api_messages = []
        for msg in messages:
            if msg.get("role") != "system":
                api_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        # Stream response
        with client.messages.stream(
            model=model,
            max_tokens=2048,
            system=system_content,
            messages=api_messages
        ) as stream:
            for text in stream.text_stream:
                yield text
    
    except ImportError:
        yield "Error: anthropic library not installed. Install with: pip install anthropic"
    except Exception as e:
        yield f"Error: {str(e)}"


# ========================
# CHATGPT (OpenAI)
# ========================

def stream_chatgpt_response(
    messages: list[dict],
    api_key: str,
    system_prompt: Optional[str] = None,
    model: str = "gpt-4o-mini"
) -> Generator[str, None, None]:
    """Stream response from ChatGPT via OpenAI API."""
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=api_key)
        
        # Prepare messages with system prompt
        api_messages = []
        if system_prompt:
            api_messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        for msg in messages:
            if msg.get("role") != "system":
                api_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        # Stream response
        stream = client.chat.completions.create(
            model=model,
            messages=api_messages,
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    except ImportError:
        yield "Error: openai library not installed. Install with: pip install openai"
    except Exception as e:
        yield f"Error: {str(e)}"


# ========================
# GROK (xAI)
# ========================

def stream_grok_response(
    messages: list[dict],
    api_key: str,
    system_prompt: Optional[str] = None,
    model: str = "grok-beta"
) -> Generator[str, None, None]:
    """Stream response from Grok via xAI API."""
    try:
        # Prepare messages
        api_messages = []
        if system_prompt:
            api_messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        for msg in messages:
            if msg.get("role") != "system":
                api_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        # Call xAI API via HTTP
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": api_messages,
            "stream": True
        }
        
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=120,
            stream=True
        )
        
        if response.status_code != 200:
            yield f"Error: xAI API returned status {response.status_code}"
            return
        
        for line in response.iter_lines():
            if line and line.startswith(b"data: "):
                try:
                    import json
                    data = json.loads(line[6:].decode())
                    if "choices" in data and data["choices"]:
                        delta = data["choices"][0].get("delta", {})
                        if "content" in delta:
                            yield delta["content"]
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
    
    except Exception as e:
        yield f"Error: {str(e)}"


# ========================
# UNIFIED INTERFACE
# ========================

def generate_response(
    messages: list[dict],
    backend: str = "ollama",
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
    api_key: Optional[str] = None
) -> Generator[str, None, None]:
    """
    Unified interface to generate responses from any backend.
    
    Args:
        messages: List of message dicts with 'role' and 'content'.
        backend: "ollama", "claude", "chatgpt", or "grok".
        model: Model name (defaults based on backend).
        system_prompt: Custom system prompt.
        api_key: API key for cloud backends.
        
    Yields:
        str: Response chunks from the selected backend.
    """
    if backend == "ollama":
        yield from stream_ollama_response(messages, model or DEFAULT_MODEL, system_prompt)
    
    elif backend == "claude":
        if not api_key:
            yield "Error: Claude API key not provided."
            return
        yield from stream_claude_response(messages, api_key, system_prompt, model or "claude-3-5-sonnet-20241022")
    
    elif backend == "chatgpt":
        if not api_key:
            yield "Error: ChatGPT API key not provided."
            return
        yield from stream_chatgpt_response(messages, api_key, system_prompt, model or "gpt-4o-mini")
    
    elif backend == "grok":
        if not api_key:
            yield "Error: Grok API key not provided."
            return
        yield from stream_grok_response(messages, api_key, system_prompt, model or "grok-beta")
    
    else:
        yield f"Error: Unknown backend '{backend}'. Use 'ollama', 'claude', 'chatgpt', or 'grok'."


def get_available_backends(claude_key: bool = False, grok_key: bool = False, openai_key: bool = False) -> list[str]:
    """
    Get list of available backends based on API keys and Ollama status.
    
    Args:
        claude_key: True if Claude API key is set.
        grok_key: True if Grok API key is set.
        openai_key: True if OpenAI API key is set.
        
    Returns:
        List of available backend names.
    """
    backends = []
    
    if check_ollama_connection():
        backends.append("Ollama (Local)")
    
    if claude_key:
        backends.append("Claude (Anthropic)")
    
    if openai_key:
        backends.append("ChatGPT (OpenAI)")
    
    if grok_key:
        backends.append("Grok (xAI)")
    
    # Fallback to Ollama if no backends available
    if not backends:
        backends.append("Ollama (Local)")
    
    return backends


def backend_to_key(backend: str) -> str:
    """Convert backend display name to backend key."""
    mapping = {
        "Ollama (Local)": "ollama",
        "Claude (Anthropic)": "claude",
        "ChatGPT (OpenAI)": "chatgpt",
        "Grok (xAI)": "grok"
    }
    return mapping.get(backend, "ollama")
