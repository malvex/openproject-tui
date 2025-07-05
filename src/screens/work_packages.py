"""Work packages screen for OpenProject TUI."""

from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import DataTable, Input, Label, LoadingIndicator, Header, Footer

from ..client import OpenProjectClient
from ..config import config
from ..models import Project, WorkPackage
from ..widgets import WorkPackagePanel


class WorkPackagesScreen(Screen):
    """Screen to display work packages for a project."""

    CSS = """
    #main_container {
        layout: grid;
        grid-size: 2 1;
        grid-columns: 1fr 0fr;
        height: 100%;
    }

    #main_container.panel-visible {
        grid-columns: 1fr 1fr;
    }


    #work_packages_table {
        width: 100%;
        height: 1fr;
        border: solid $primary;
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
        ("q", "quit", "Quit"),
        ("escape", "escape_action", "Back/Close"),
        ("r", "refresh", "Refresh"),
        ("enter", "select_work_package", "Toggle Details"),
        ("/", "toggle_search", "Search"),
        ("n", "new_work_package", "New"),
        ("e", "edit_work_package", "Edit"),
    ]

    def __init__(self, project: Project):
        """Initialize the work packages screen."""
        super().__init__()
        self.project = project
        self.client = OpenProjectClient(api_url=config.api_url, api_key=config.api_key)
        self.work_packages = []
        self.filtered_work_packages = []
        self.search_query = ""
        self.selected_work_package: Optional[WorkPackage] = None

        self.sub_title = f"Work Packages - {project.name}"

    def compose(self) -> ComposeResult:
        """Compose the work packages screen layout."""
        yield Header()
        yield Footer()

        with Container(id="main_container"):
            with Container(id="list_container"):
                yield Input(
                    placeholder="Search work packages...",
                    id="search_input",
                    classes="hidden",
                )

                yield DataTable(id="work_packages_table", cursor_type="row")
                yield LoadingIndicator(id="loading")
                yield Label("", id="error", classes="hidden")
                yield Label(
                    "No work packages found for this project", id="empty_message"
                )

            yield WorkPackagePanel(id="details_panel")

    async def on_mount(self) -> None:
        """Load work packages when screen is mounted."""
        table = self.query_one("#work_packages_table", DataTable)

        table.add_column("ID", width=8)
        table.add_column("Subject", width=50)
        table.add_column("Status", width=15)
        table.add_column("Type", width=15)
        table.add_column("Priority", width=10)
        table.add_column("Assignee", width=20)

        await self.load_work_packages()

    async def load_work_packages(self) -> None:
        """Load work packages from the API."""
        table = self.query_one("#work_packages_table", DataTable)
        loading = self.query_one("#loading", LoadingIndicator)
        error_label = self.query_one("#error", Label)
        empty_label = self.query_one("#empty_message", Label)

        loading.display = True
        table.display = False
        error_label.display = False
        empty_label.display = False

        try:
            self.work_packages = await self.client.get_work_packages(
                project_id=self.project.id
            )
            self.filtered_work_packages = self.work_packages.copy()

            self._update_table()

            loading.display = False

        except Exception as e:
            loading.display = False
            error_label.display = True
            error_label.update(f"Error loading work packages: {str(e)}")

    async def action_refresh(self) -> None:
        """Refresh the work packages list."""
        await self.load_work_packages()

    async def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()

    async def action_escape_action(self) -> None:
        """Handle escape key with priority: search -> panel -> back."""
        search_input = self.query_one("#search_input", Input)
        main_container = self.query_one("#main_container")

        if not search_input.has_class("hidden"):
            await self.action_toggle_search()
        elif main_container.has_class("panel-visible"):
            await self.action_close_panel()
        else:
            self.app.pop_screen()

    async def action_select_work_package(self) -> None:
        """Toggle work package details panel."""
        table = self.query_one("#work_packages_table", DataTable)
        if table.cursor_row is not None and table.cursor_row < len(
            self.filtered_work_packages
        ):
            selected_wp = self.filtered_work_packages[table.cursor_row]
            panel = self.query_one("#details_panel", WorkPackagePanel)
            main_container = self.query_one("#main_container")

            if (
                main_container.has_class("panel-visible")
                and self.selected_work_package == selected_wp
            ):
                # Hide panel if already showing this work package
                await self.action_close_panel()
            else:
                # Show panel with selected work package
                self.selected_work_package = selected_wp
                main_container.add_class("panel-visible")
                panel.work_package = selected_wp

    @on(DataTable.RowSelected)
    async def on_datatable_row_selected(self) -> None:
        """Handle row selection in the data table."""
        await self.action_select_work_package()

    @on(DataTable.RowHighlighted)
    async def on_datatable_row_highlighted(
        self, event: DataTable.RowHighlighted
    ) -> None:
        """Handle row highlighting - update panel as user navigates."""
        if event.row_key is not None:
            row_index = event.cursor_row
            if 0 <= row_index < len(self.filtered_work_packages):
                work_package = self.filtered_work_packages[row_index]
                panel = self.query_one("#details_panel", WorkPackagePanel)
                main_container = self.query_one("#main_container")

                # Only update if panel is visible
                if main_container.has_class("panel-visible"):
                    panel.work_package = work_package
                    self.selected_work_package = work_package

    async def on_unmount(self) -> None:
        """Clean up when screen is unmounted."""
        await self.client.close()

    async def action_new_work_package(self) -> None:
        """Create a new work package."""
        from .work_package_form import WorkPackageFormScreen

        def on_dismiss(result: Optional[WorkPackage]) -> None:
            if result:
                self.call_after_refresh(self.load_work_packages)

        self.app.push_screen(WorkPackageFormScreen(self.project), on_dismiss)

    async def action_toggle_search(self) -> None:
        """Toggle search input visibility."""
        search_input = self.query_one("#search_input", Input)

        if not search_input.has_class("hidden"):
            search_input.add_class("hidden")
            search_input.value = ""
            self.search_query = ""
            self._update_table()
            table = self.query_one("#work_packages_table", DataTable)
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
        """Handle search submission - focus on table."""
        table = self.query_one("#work_packages_table", DataTable)
        table.focus()

    def _update_table(self) -> None:
        """Update table with filtered work packages."""
        table = self.query_one("#work_packages_table", DataTable)
        empty_label = self.query_one("#empty_message", Label)
        search_input = self.query_one("#search_input", Input)

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

        table.clear()

        if not self.filtered_work_packages:
            table.display = False
            empty_label.display = True
            return

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

        # Keep focus on search input during active search
        if not (not search_input.has_class("hidden") and search_input.has_focus):
            if self.filtered_work_packages and table.row_count > 0:
                table.focus()

    async def action_close_panel(self) -> None:
        """Close the details panel."""
        panel = self.query_one("#details_panel", WorkPackagePanel)
        main_container = self.query_one("#main_container")

        main_container.remove_class("panel-visible")
        panel.work_package = None
        self.selected_work_package = None

        table = self.query_one("#work_packages_table", DataTable)
        table.focus()

    async def action_edit_work_package(self) -> None:
        """Edit the selected work package."""
        if not self.selected_work_package:
            return

        from .work_package_form import WorkPackageFormScreen

        def on_dismiss(result: Optional[WorkPackage]) -> None:
            if result:
                self.selected_work_package = result
                panel = self.query_one("#details_panel", WorkPackagePanel)
                panel.work_package = result
                self.call_after_refresh(self.load_work_packages)

        self.app.push_screen(
            WorkPackageFormScreen(self.project, self.selected_work_package), on_dismiss
        )
