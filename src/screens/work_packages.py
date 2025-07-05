"""Work packages screen for OpenProject TUI."""

from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import DataTable, Input, Label, LoadingIndicator
from textual.events import Key

from ..client import OpenProjectClient
from ..config import config
from ..models import Project, WorkPackage


class WorkPackagesScreen(Screen):
    """Screen to display work packages for a project."""

    CSS = """
    WorkPackagesScreen {
        align: center middle;
    }

    #header {
        height: 3;
        background: $surface;
        padding: 1;
        border-bottom: solid $primary;
    }

    #project_name {
        text-style: bold;
    }

    #work_packages_table {
        width: 100%;
        height: 100%;
    }

    #loading {
        display: none;
    }

    #error {
        color: $error;
        display: none;
        text-align: center;
        margin: 2;
    }

    #empty_message {
        text-align: center;
        margin: 2;
        display: none;
    }

    .hidden {
        display: none;
    }

    #search_input {
        margin: 1 2;
        display: block;
    }

    #search_input.hidden {
        display: none;
    }
    """

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("r", "refresh", "Refresh"),
        ("enter", "select_work_package", "View Details"),
        ("/", "toggle_search", "Search"),
        ("n", "new_work_package", "New"),
    ]

    def __init__(self, project: Project):
        """Initialize the work packages screen."""
        super().__init__()
        self.project = project
        self.client = OpenProjectClient(api_url=config.api_url, api_key=config.api_key)
        self.work_packages = []
        self.filtered_work_packages = []
        self.search_query = ""

    def compose(self) -> ComposeResult:
        """Compose the work packages screen layout."""
        with Container():
            with Horizontal(id="header"):
                yield Label(f"Work Packages - {self.project.name}", id="project_name")

            # Search input
            yield Input(
                placeholder="Search work packages...",
                id="search_input",
                classes="hidden",
            )

            yield DataTable(id="work_packages_table", cursor_type="row")
            yield LoadingIndicator(id="loading")
            yield Label("", id="error", classes="hidden")
            yield Label("No work packages found for this project", id="empty_message")

    async def on_mount(self) -> None:
        """Load work packages when screen is mounted."""
        table = self.query_one("#work_packages_table", DataTable)

        # Set up table columns
        table.add_column("ID", width=8)
        table.add_column("Subject", width=50)
        table.add_column("Status", width=15)
        table.add_column("Type", width=15)
        table.add_column("Priority", width=10)
        table.add_column("Assignee", width=20)

        # Load work packages
        await self.load_work_packages()

    async def load_work_packages(self) -> None:
        """Load work packages from the API."""
        table = self.query_one("#work_packages_table", DataTable)
        loading = self.query_one("#loading", LoadingIndicator)
        error_label = self.query_one("#error", Label)
        empty_label = self.query_one("#empty_message", Label)

        # Reset visibility
        loading.display = True
        table.display = False
        error_label.display = False
        empty_label.display = False

        try:
            # Fetch work packages for the project
            self.work_packages = await self.client.get_work_packages(
                project_id=self.project.id
            )
            self.filtered_work_packages = self.work_packages.copy()

            # Update table with filtered work packages
            self._update_table()

            # Show table
            loading.display = False

        except Exception as e:
            # Show error
            loading.display = False
            error_label.display = True
            error_label.update(f"Error loading work packages: {str(e)}")

    async def action_refresh(self) -> None:
        """Refresh the work packages list."""
        await self.load_work_packages()

    async def action_go_back(self) -> None:
        """Go back to the main screen."""
        self.app.pop_screen()

    async def action_select_work_package(self) -> None:
        """Select a work package to view details."""
        table = self.query_one("#work_packages_table", DataTable)
        if table.cursor_row is not None and table.cursor_row < len(
            self.filtered_work_packages
        ):
            selected_wp = self.filtered_work_packages[table.cursor_row]
            from .work_package_details import WorkPackageDetailsScreen

            # Pass the project we already have
            self.app.push_screen(WorkPackageDetailsScreen(selected_wp, self.project))

    @on(DataTable.RowSelected)
    async def on_datatable_row_selected(self) -> None:
        """Handle row selection in the data table."""
        await self.action_select_work_package()

    async def on_unmount(self) -> None:
        """Clean up when screen is unmounted."""
        await self.client.close()

    async def action_new_work_package(self) -> None:
        """Create a new work package."""
        from .work_package_form import WorkPackageFormScreen

        def on_dismiss(result: Optional[WorkPackage]) -> None:
            """Handle form dismissal."""
            if result:
                # Refresh the list to show the new work package
                self.call_after_refresh(self.load_work_packages)

        self.app.push_screen(WorkPackageFormScreen(self.project), on_dismiss)

    async def action_toggle_search(self) -> None:
        """Toggle search input visibility."""
        search_input = self.query_one("#search_input", Input)

        if not search_input.has_class("hidden"):
            # Hide search
            search_input.add_class("hidden")
            search_input.value = ""
            self.search_query = ""
            self._update_table()
            # Focus table
            table = self.query_one("#work_packages_table", DataTable)
            table.focus()
        else:
            # Show search
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
        """Handle search submission - focus on table."""
        table = self.query_one("#work_packages_table", DataTable)
        table.focus()

    async def on_key(self, event: Key) -> None:
        """Handle key events."""
        # If search is visible and ESC is pressed, hide it
        if event.key == "escape":
            search_input = self.query_one("#search_input", Input)
            if not search_input.has_class("hidden"):
                await self.action_toggle_search()
                event.stop()

    def _update_table(self) -> None:
        """Update table with filtered work packages."""
        table = self.query_one("#work_packages_table", DataTable)
        empty_label = self.query_one("#empty_message", Label)
        search_input = self.query_one("#search_input", Input)

        # Filter work packages
        if self.search_query:
            self.filtered_work_packages = [
                wp
                for wp in self.work_packages
                if self.search_query in wp.subject.lower()
                or (wp.status and self.search_query in wp.status.name.lower())
                or (wp.assignee and self.search_query in wp.assignee.name.lower())
            ]
        else:
            self.filtered_work_packages = self.work_packages.copy()

        # Update table
        table.clear()

        if not self.filtered_work_packages:
            # Show empty state
            table.display = False
            empty_label.display = True
            return

        # Hide empty state
        empty_label.display = False
        table.display = True

        for wp in self.filtered_work_packages:
            table.add_row(
                str(wp.id),
                wp.subject,
                wp.status.name if wp.status else "N/A",
                wp.type.name if wp.type else "N/A",
                wp.priority.name if wp.priority else "N/A",
                wp.assignee.name if wp.assignee else "Unassigned",
            )

        # Don't change focus if search input is visible and has focus
        if not (not search_input.has_class("hidden") and search_input.has_focus):
            # Focus on table if we have work packages
            if self.filtered_work_packages and table.row_count > 0:
                table.focus()
