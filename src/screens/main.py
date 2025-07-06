"""Main screen for OpenProject TUI."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import DataTable, Label, LoadingIndicator
from textual.binding import Binding

from ..client import OpenProjectClient
from ..config import config


class MainScreen(Screen):
    """Main screen showing projects and navigation."""

    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
        Binding("enter", "select_project", "Select Project"),
        Binding("q", "quit", "Quit"),
    ]

    CSS = """
    MainScreen {
        background: $surface;
    }

    #header {
        height: 3;
        background: $primary;
        color: $text;
        padding: 1;
    }

    #projects_table {
        height: 100%;
        border: solid $primary;
    }

    #loading {
        align: center middle;
    }

    #error {
        color: $error;
        text-align: center;
        margin: 2;
    }
    """

    def __init__(self):
        """Initialize the main screen."""
        super().__init__()
        self.client = OpenProjectClient(api_url=config.api_url, api_key=config.api_key)
        self.projects = []

    def compose(self) -> ComposeResult:
        """Compose the main screen layout."""
        with Container():
            with Horizontal(id="header"):
                yield Label("OpenProject TUI", classes="title")
                yield Label(f"Connected to: {config.api_url}", classes="subtitle")

            yield DataTable(id="projects_table", cursor_type="row")
            yield LoadingIndicator(id="loading")
            yield Label("", id="error", classes="hidden")

    async def on_mount(self) -> None:
        """Load projects when screen is mounted."""
        table = self.query_one("#projects_table", DataTable)

        # Set up table columns
        table.add_column("ID", width=6)
        table.add_column("Identifier", width=20)
        table.add_column("Name", width=40)
        table.add_column("Status", width=10)
        table.add_column("Public", width=8)

        # Load projects
        await self.load_projects()

    async def load_projects(self) -> None:
        """Load projects from the API."""
        table = self.query_one("#projects_table", DataTable)
        loading = self.query_one("#loading", LoadingIndicator)
        error_label = self.query_one("#error", Label)

        # Show loading indicator
        loading.display = True
        table.display = False
        error_label.display = False

        try:
            # Fetch projects
            self.projects = await self.client.get_projects()

            # Clear and populate table
            table.clear()
            for project in self.projects:
                # Add row without classes parameter
                table.add_row(
                    str(project.id),
                    project.identifier,
                    project.name,
                    "Active" if project.active else "Inactive",
                    "Yes" if project.public else "No",
                )

            # Show table
            loading.display = False
            table.display = True

            # Focus on table if we have projects
            if self.projects:
                table.focus()

        except Exception as e:
            # Show error
            loading.display = False
            error_label.display = True
            error_label.update(f"Error loading projects: {str(e)}")

    async def action_refresh(self) -> None:
        """Refresh the projects list."""
        await self.load_projects()

    async def action_select_project(self) -> None:
        """Select the current project and show work packages."""
        table = self.query_one("#projects_table", DataTable)
        if table.cursor_row is not None and table.cursor_row < len(self.projects):
            selected_project = self.projects[table.cursor_row]
            # TODO: Navigate to work packages screen
            self.app.notify(f"Selected project: {selected_project.name}")

    async def on_unmount(self) -> None:
        """Clean up when screen is unmounted."""
        await self.client.close()
