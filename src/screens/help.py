"""Help screen for OpenProject TUI."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Label


class HelpScreen(Screen):
    """Screen to display keyboard shortcuts and help information."""

    CSS = """
    HelpScreen {
        align: center middle;
    }

    #help_container {
        width: 80;
        height: 90%;
        background: $surface;
        border: thick $primary;
        padding: 2;
    }

    #help_title {
        text-style: bold;
        text-align: center;
        color: $primary;
        margin-bottom: 2;
    }

    #shortcuts_container {
        overflow-y: auto;
    }

    .section-title {
        text-style: bold;
        color: $secondary;
        margin-top: 2;
        margin-bottom: 1;
    }

    .shortcut-row {
        height: 1;
        margin-bottom: 1;
    }

    .key {
        width: 20;
        color: $warning;
        text-style: bold;
    }

    .description {
        color: $text;
    }
    """

    BINDINGS = [
        ("escape", "close", "Close"),
        ("q", "close", "Close"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the help screen layout."""
        with Container(id="help_container"):
            yield Label("OpenProject TUI - Keyboard Shortcuts", id="help_title")

            with Vertical(id="shortcuts_container"):
                # Global shortcuts
                yield Label("Global Shortcuts", classes="section-title")
                yield from self._create_shortcut_row("?", "Show this help screen")
                yield from self._create_shortcut_row("q", "Quit application")
                yield from self._create_shortcut_row("ESC", "Go back / Cancel")

                # Navigation shortcuts
                yield Label("Navigation", classes="section-title")
                yield from self._create_shortcut_row("↑/↓", "Move up/down in lists")
                yield from self._create_shortcut_row("Enter", "Select item / Open")
                yield from self._create_shortcut_row("Tab", "Focus next element")
                yield from self._create_shortcut_row(
                    "Shift+Tab", "Focus previous element"
                )

                # Screen-specific shortcuts
                yield Label("Projects Screen", classes="section-title")
                yield from self._create_shortcut_row("r", "Refresh projects list")
                yield from self._create_shortcut_row(
                    "Enter", "View project work packages"
                )

                yield Label("Work Packages Screen", classes="section-title")
                yield from self._create_shortcut_row("r", "Refresh work packages")
                yield from self._create_shortcut_row(
                    "Enter", "View work package details"
                )
                yield from self._create_shortcut_row("ESC", "Back to projects")

                yield Label("Work Package Details", classes="section-title")
                yield from self._create_shortcut_row("ESC", "Back to work packages")

                # Future shortcuts (commented in UI)
                yield Label("Coming Soon", classes="section-title")
                yield from self._create_shortcut_row(
                    "/", "Search (not yet implemented)"
                )
                yield from self._create_shortcut_row(
                    "n", "New work package (not yet implemented)"
                )
                yield from self._create_shortcut_row("e", "Edit (not yet implemented)")

    def _create_shortcut_row(self, key: str, description: str):
        """Create a row showing a keyboard shortcut."""
        with Horizontal(classes="shortcut-row"):
            yield Label(key, classes="key")
            yield Label(description, classes="description")

    async def action_close(self) -> None:
        """Close the help screen."""
        self.app.pop_screen()
