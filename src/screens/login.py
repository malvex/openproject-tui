"""Login screen for OpenProject TUI."""

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Label

from ..client import OpenProjectClient, AuthenticationError, APIError
from ..config import config


class LoginScreen(Screen):
    """Login screen for authentication."""

    CSS = """
    LoginScreen {
        align: center middle;
    }

    #login_container {
        width: 60;
        height: auto;
        border: thick $primary;
        padding: 2 4;
    }

    #login_title {
        text-align: center;
        text-style: bold;
        margin-bottom: 2;
    }

    Input {
        margin-bottom: 1;
    }

    #error_message {
        color: $error;
        text-align: center;
        margin-top: 1;
        display: none;
    }

    #error_message.visible {
        display: block;
    }

    #login_button {
        width: 100%;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the login screen."""
        with Container(id="login_container"):
            yield Label("OpenProject Login", id="login_title")
            with Vertical():
                yield Input(
                    placeholder="https://openproject.example.com",
                    id="api_url",
                    value=config.api_url.replace("/api/v3", "")
                    if config.api_url
                    else "",
                )
                yield Input(
                    placeholder="Your API key",
                    password=True,
                    id="api_key",
                    value=config.api_key,
                )
                yield Button("Login", variant="primary", id="login_button")
                yield Label("", id="error_message")

    def on_mount(self) -> None:
        """Focus the first input on mount."""
        self.query_one("#api_url").focus()

    @on(Button.Pressed, "#login_button")
    async def handle_login(self) -> None:
        """Handle login button press."""
        error_label = self.query_one("#error_message", Label)
        error_label.remove_class("visible")

        api_url_input = self.query_one("#api_url", Input)
        api_key_input = self.query_one("#api_key", Input)

        api_url = api_url_input.value.strip()
        api_key = api_key_input.value.strip()

        # Validate inputs
        if not api_url or not api_key:
            error_label.update("Please fill in all fields")
            error_label.add_class("visible")
            return

        # Ensure URL ends with /api/v3
        if not api_url.endswith("/api/v3"):
            api_url = f"{api_url.rstrip('/')}/api/v3"

        # Test connection
        try:
            client = OpenProjectClient(api_url=api_url, api_key=api_key)
            await client.test_connection()
            await client.close()

            # Save configuration
            config.api_url = api_url
            config.api_key = api_key

            # Save to .env file for persistence
            await self._save_config(api_url, api_key)

            # Navigate to main screen
            from .main import MainScreen

            self.app.pop_screen()
            self.app.push_screen(MainScreen())

        except AuthenticationError as e:
            error_label.update(str(e))
            error_label.add_class("visible")
        except APIError as e:
            error_label.update(f"Connection failed: {str(e)}")
            error_label.add_class("visible")
        except Exception as e:
            error_label.update(f"Unexpected error: {str(e)}")
            error_label.add_class("visible")

    async def _save_config(self, api_url: str, api_key: str) -> None:
        """Save configuration to .env file."""
        env_path = config.config_dir / ".env"
        env_content = f"""# OpenProject API Configuration
OPENPROJECT_API_URL={api_url}
OPENPROJECT_API_KEY={api_key}

# Request timeout in seconds
OPENPROJECT_TIMEOUT={config.timeout}

# Default page size for pagination
OPENPROJECT_PAGE_SIZE={config.page_size}
"""
        env_path.write_text(env_content)
