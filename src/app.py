"""Main Textual application for OpenProject TUI."""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Welcome


class OpenProjectApp(App):
    """Main OpenProject TUI application."""

    TITLE = "OpenProject TUI"
    SUB_TITLE = "Terminal User Interface for OpenProject"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header()
        yield Welcome()
        yield Footer()

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


if __name__ == "__main__":
    app = OpenProjectApp()
    app.run()
