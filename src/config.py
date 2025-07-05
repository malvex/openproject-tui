"""Configuration management for OpenProject TUI."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


class Config:
    """Application configuration."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        load_dotenv()

        self.api_url = os.getenv("OPENPROJECT_API_URL", "")
        self.api_key = os.getenv("OPENPROJECT_API_KEY", "")
        self.timeout = int(os.getenv("OPENPROJECT_TIMEOUT", "30"))
        self.page_size = int(os.getenv("OPENPROJECT_PAGE_SIZE", "25"))

        # Paths
        self.cache_dir = Path.home() / ".cache" / "openproject-tui"
        self.config_dir = Path.home() / ".config" / "openproject-tui"

        # Create directories if they don't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

    @property
    def is_configured(self) -> bool:
        """Check if the API is properly configured."""
        return bool(self.api_url and self.api_key)

    def validate(self) -> Optional[str]:
        """Validate configuration and return error message if invalid."""
        if not self.api_url:
            return "OpenProject API URL not configured"
        if not self.api_key:
            return "OpenProject API key not configured"
        if not self.api_url.startswith(("http://", "https://")):
            return "Invalid API URL format"
        return None


# Global configuration instance
config = Config()
