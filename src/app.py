"""Main Textual application for OpenProject TUI."""

from textual.app import App, ComposeResult

from .config import config
from .screens.login import LoginScreen
from .screens.main import MainScreen


class OpenProjectApp(App):
    """Main OpenProject TUI application."""

    TITLE = "OpenProject TUI"
    SUB_TITLE = "Terminal User Interface for OpenProject"

    CSS = """
    Screen {
        background: $surface;
    }
    """

    BINDINGS = [
        ("?", "show_help", "Help"),
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        # Empty list required by Textual - screens compose their own widgets
        return []

    def on_mount(self) -> None:
        """Check configuration on mount."""
        if not config.is_configured:
            self.push_screen(LoginScreen())
        else:
            self.push_screen(MainScreen())

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_show_help(self) -> None:
        """Show the help screen."""
        from .screens.help import HelpScreen

        self.push_screen(HelpScreen())


if __name__ == "__main__":
    app = OpenProjectApp()
    app.run()
