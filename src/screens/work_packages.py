"""Work packages screen for OpenProject TUI."""

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen
from textual.widgets import DataTable, Label, LoadingIndicator

from ..client import OpenProjectClient
from ..config import config
from ..models import Project


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
    """

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("r", "refresh", "Refresh"),
        ("enter", "select_work_package", "View Details"),
    ]

    def __init__(self, project: Project):
        """Initialize the work packages screen."""
        super().__init__()
        self.project = project
        self.client = OpenProjectClient(api_url=config.api_url, api_key=config.api_key)
        self.work_packages = []

    def compose(self) -> ComposeResult:
        """Compose the work packages screen layout."""
        with Container():
            with Horizontal(id="header"):
                yield Label(f"Work Packages - {self.project.name}", id="project_name")

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

            # Clear and populate table
            table.clear()

            if not self.work_packages:
                # Show empty state
                loading.display = False
                empty_label.display = True
                return

            for wp in self.work_packages:
                table.add_row(
                    str(wp.id),
                    wp.subject,
                    wp.status.name if wp.status else "N/A",
                    wp.type.name if wp.type else "N/A",
                    wp.priority.name if wp.priority else "N/A",
                    wp.assignee.name if wp.assignee else "Unassigned",
                )

            # Show table
            loading.display = False
            table.display = True

            # Focus on table if we have work packages
            if self.work_packages:
                table.focus()

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
        if table.cursor_row is not None and table.cursor_row < len(self.work_packages):
            selected_wp = self.work_packages[table.cursor_row]
            from .work_package_details import WorkPackageDetailsScreen

            self.app.push_screen(WorkPackageDetailsScreen(selected_wp))

    @on(DataTable.RowSelected)
    async def on_datatable_row_selected(self) -> None:
        """Handle row selection in the data table."""
        await self.action_select_work_package()

    async def on_unmount(self) -> None:
        """Clean up when screen is unmounted."""
        await self.client.close()
