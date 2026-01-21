"""
Ollama integration helper functions for AI assistant builder.
"""

import os
from typing import Generator, Optional
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3")


def check_connection() -> bool:
    """
    Check if Ollama server is running and accessible.
    
    Returns:
        bool: True if connection successful, False otherwise.
    """
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        return response.status_code == 200
    except (requests.RequestException, Exception):
        return False


def list_models() -> list[str]:
    """
    Fetch list of available models from Ollama.
    
    Returns:
        list[str]: List of available model names, or empty list if error.
    """
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            # Extract model names, handling both old and new API formats
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


def generate_response(
    messages: list[dict],
    model: str = DEFAULT_MODEL,
    system_prompt: Optional[str] = None
) -> Generator[str, None, None]:
    """
    Stream response from Ollama for given messages.
    
    Args:
        messages: List of message dicts with 'role' and 'content' keys.
        model: Model name to use (default from .env or llama3).
        system_prompt: Optional system prompt to prefix conversation.
        
    Yields:
        str: Streamed response chunks from the model.
    """
    try:
        # If system prompt provided and not already in messages, add it
        if system_prompt:
            # Check if system message already exists
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
        
        # Stream the response
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
        yield "Error: Request to Ollama timed out. Is the model running?"
    except requests.exceptions.ConnectionError:
        yield "Error: Could not connect to Ollama. Is it running at " + OLLAMA_HOST + "?"
    except Exception as e:
        yield f"Error: {str(e)}"


def pull_model(model: str) -> Generator[str, None, None]:
    """
    Pull a model from Ollama registry.
    
    Args:
        model: Model name to pull.
        
    Yields:
        str: Status messages during the pull.
    """
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
