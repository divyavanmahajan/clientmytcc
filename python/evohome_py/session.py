"""Session management for the CLI."""

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Optional, List

@dataclass
class Session:
    """Session data structure."""
    email: str
    cookies: List[str]

def get_session_path() -> Path:
    """Get the path to the session file."""
    config_dir = Path.home() / ".config" / "evohome_py"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "session.json"

def save_session(email: str, cookies: Dict[str, str]) -> None:
    """Save the session to disk.
    
    Args:
        email: User email
        cookies: Dictionary of cookies
    """
    # Convert dict to list of "key=value" strings for Rust compatibility
    cookie_list = [f"{k}={v}" for k, v in cookies.items()]
    session = Session(email=email, cookies=cookie_list)
    path = get_session_path()
    with open(path, "w") as f:
        json.dump(asdict(session), f, indent=2)

def load_session() -> Optional[Session]:
    """Load the session from disk."""
    path = get_session_path()
    if not path.exists():
        return None
    
    try:
        with open(path, "r") as f:
            data = json.load(f)
            # Handle both formats (List[str] from Rust/New Python, Dict from Old Python)
            cookies = data.get("cookies", [])
            if isinstance(cookies, dict):
                cookies = [f"{k}={v}" for k, v in cookies.items()]
            
            return Session(email=data["email"], cookies=cookies)
    except (json.JSONDecodeError, KeyError, OSError):
        return None

def cookies_to_dict(cookie_list: List[str]) -> Dict[str, str]:
    """Convert list of cookie strings to dictionary."""
    cookies = {}
    from http.cookies import SimpleCookie
    
    for cookie_str in cookie_list:
        try:
            # Simple parsing for "key=value" or full Set-Cookie strings
            if "=" in cookie_str:
                # Use SimpleCookie to handle complex strings with attributes
                c = SimpleCookie()
                c.load(cookie_str)
                for key, morsel in c.items():
                    cookies[key] = morsel.value
        except Exception:
            continue
            
    return cookies

def clear_session() -> None:
    """Clear the stored session."""
    path = get_session_path()
    if path.exists():
        try:
            os.remove(path)
        except OSError:
            pass
