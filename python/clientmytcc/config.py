"""Configuration management for CLI."""

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Fallback for older Python
    except ImportError:
        tomllib = None

try:
    import tomli_w
except ImportError:
    tomli_w = None

from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Manage CLI configuration using TOML format (shared with Rust CLI)."""
    
    def __init__(self):
        """Initialize configuration manager."""
        self.config_dir = Path.home() / ".config" / "evohome"
        self.config_file = self.config_dir / "config.toml"
        self._data: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from TOML file."""
        if self.config_file.exists():
            try:
                if tomllib is None:
                    # Fallback to simple parsing if tomllib not available
                    self._data = self._parse_simple_toml(self.config_file.read_text())
                else:
                    with open(self.config_file, "rb") as f:
                        self._data = tomllib.load(f)
            except Exception:
                self._data = {}
        return self._data
    
    def save(self) -> None:
        """Save configuration to TOML file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        if tomli_w is None:
            # Fallback to simple TOML writing
            content = self._write_simple_toml(self._data)
            self.config_file.write_text(content)
        else:
            with open(self.config_file, "wb") as f:
                tomli_w.dump(self._data, f)
    
    def get(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        """Get a configuration value."""
        return self._data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value."""
        self._data[key] = value
    
    def clear(self) -> None:
        """Clear all configuration."""
        self._data = {}
    
    @staticmethod
    def _parse_simple_toml(content: str) -> Dict[str, Any]:
        """Simple TOML parser for basic key=value pairs (fallback)."""
        data = {}
        for line in content.strip().split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                data[key] = value
        return data
    
    @staticmethod
    def _write_simple_toml(data: Dict[str, Any]) -> str:
        """Simple TOML writer for basic key=value pairs (fallback)."""
        lines = []
        for key, value in data.items():
            if isinstance(value, str):
                lines.append(f'{key} = "{value}"')
            else:
                lines.append(f'{key} = {value}')
        return '\n'.join(lines) + '\n'
