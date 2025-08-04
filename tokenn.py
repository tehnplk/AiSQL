"""
Token configuration module for centralized API key management.
Reads all API keys and tokens from token.txt file.
"""
from typing import Dict


def load_tokens() -> Dict[str, str]:
    """Load all tokens and API keys from token.txt file."""
    tokens = {}
    token_file = 'token.txt'
    
    try:
        with open(token_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    tokens[key.strip()] = value.strip().strip('"\'')
    except FileNotFoundError:
        print(f"Warning: token.txt file not found at {token_file}")
    except Exception as e:
        print(f"Error reading token.txt: {e}")
    
    return tokens


def get_token(key_name: str, default: str = "") -> str:
    """Get specific token value by key name."""
    tokens = load_tokens()
    return tokens.get(key_name, default)


# Predefined token accessors
def get_logfire_token() -> str:
    """Get Logfire token."""
    return get_token('LOGFIRE_TOKEN')


def get_openrouter_key() -> str:
    """Get OpenRouter API key."""
    return get_token('OPENROUTER_API_KEY')


def get_gemini_key() -> str:
    """Get Gemini API key."""
    return get_token('GEMINI_API_KEY')

def get_openai_key() -> str:
    """Get OpenAI API key."""
    return get_token('OPENAI_API_KEY')

# Load all tokens at import time
TOKENS = load_tokens()

# Export commonly used tokens
LOGFIRE_KEY = get_logfire_token()
OPENROUTER_API_KEY = get_openrouter_key()
GEMINI_API_KEY = get_gemini_key()
OPENAI_API_KEY = get_openai_key()

