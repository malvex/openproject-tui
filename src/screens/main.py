"""Main screen for OpenProject TUI."""

from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import DataTable, Input, Label, LoadingIndicator, Header, Footer
from textual.binding import Binding
from textual.events import Key

from ..client import OpenProjectClient
from ..config import config


class MainScreen(Screen):
    """Main screen showing projects and navigation."""

    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
        Binding("enter", "select_project", "Select Project"),
        Binding("/", "toggle_search", "Search"),
        Binding("q", "quit", "Quit"),
    ]

    CSS = """
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

    #search_input {
        margin: 1 2;
        display: block;
    }

    #search_input.hidden {
        display: none;
    }

    .hidden {
        display: none;
    }
    """

    def __init__(self):
        """Initialize the main screen."""
        super().__init__()
        self.client = OpenProjectClient(api_url=config.api_url, api_key=config.api_key)
        self.projects = []
        self.filtered_projects = []
        self.search_query = ""

    def compose(self) -> ComposeResult:
        """Compose the main screen layout."""
        yield Header()
        yield Footer()

        with Container():
            yield Input(
                placeholder="Search projects...", id="search_input", classes="hidden"
            )

            yield DataTable(id="projects_table", cursor_type="row")
            yield LoadingIndicator(id="loading")
            yield Label("", id="error", classes="hidden")

    async def on_mount(self) -> None:
        """Load projects when screen is mounted."""
        table = self.query_one("#projects_table", DataTable)

        table.add_column("ID", width=6)
        table.add_column("Identifier", width=20)
        table.add_column("Name", width=40)
        table.add_column("Status", width=10)
        table.add_column("Public", width=8)

        await self.load_projects()

    async def load_projects(self) -> None:
        """Load projects from the API."""
        table = self.query_one("#projects_table", DataTable)
        loading = self.query_one("#loading", LoadingIndicator)
        error_label = self.query_one("#error", Label)

        loading.display = True
        table.display = False
        error_label.display = False

        try:
            self.projects = await self.client.get_projects(active=True)
            self.filtered_projects = self.projects.copy()

            self._update_table()

            loading.display = False
            table.display = True

        except Exception as e:
            loading.display = False
            error_label.display = True
            error_label.update(f"Error loading projects: {str(e)}")

    async def action_refresh(self) -> None:
        """Refresh the projects list."""
        await self.load_projects()

    async def action_select_project(self) -> None:
        """Select the current project and show work packages."""
        table = self.query_one("#projects_table", DataTable)
        if table.cursor_row is not None and table.cursor_row < len(
            self.filtered_projects
        ):
            selected_project = self.filtered_projects[table.cursor_row]
            from .work_packages import WorkPackagesScreen

            self.app.push_screen(WorkPackagesScreen(selected_project))

    @on(DataTable.RowSelected)
    async def on_datatable_row_selected(self) -> None:
        """Handle row selection in the data table."""
        await self.action_select_project()

    async def on_unmount(self) -> None:
        """Clean up when screen is unmounted."""
        await self.client.close()

    async def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    async def action_toggle_search(self) -> None:
        """Toggle search input visibility."""
        search_input = self.query_one("#search_input", Input)

        if not search_input.has_class("hidden"):
            search_input.add_class("hidden")
            search_input.value = ""
            self.search_query = ""
            self._update_table()
            table = self.query_one("#projects_table", DataTable)
            table.focus()
        else:
            search_input.remove_class("hidden")
            search_input.focus()

    @on(Input.Changed)
    async def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search_input":
            self.search_query = event.value.lower()
            self._update_table()

    @on(Input.Submitted)
    async def on_search_submitted(self) -> None:
        """Handle search submission."""
        table = self.query_one("#projects_table", DataTable)
        table.focus()

    async def on_key(self, event: Key) -> None:
        """Handle key events."""
        if event.key == "escape":
            search_input = self.query_one("#search_input", Input)
            if not search_input.has_class("hidden"):
                await self.action_toggle_search()
                event.stop()

    def _update_table(self) -> None:
        """Update table with filtered projects."""
        table = self.query_one("#projects_table", DataTable)
        search_input = self.query_one("#search_input", Input)

        if self.search_query:
            self.filtered_projects = [
                p
                for p in self.projects
                if self.search_query in p.name.lower()
                or self.search_query in p.identifier.lower()
            ]
        else:
            self.filtered_projects = self.projects.copy()

        table.clear()
        for project in self.filtered_projects:
            table.add_row(
                str(project.id),
                project.identifier,
                project.name,
                "Active" if project.active else "Inactive",
                "Yes" if project.public else "No",
            )

        # Keep focus on search input during active search
        if not (not search_input.has_class("hidden") and search_input.has_focus):
            if self.filtered_projects and table.row_count > 0:
                table.focus()
