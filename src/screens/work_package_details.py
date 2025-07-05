"""Work package details screen for OpenProject TUI."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Label, ProgressBar, Static

from ..models import WorkPackage


class WorkPackageDetailsScreen(Screen):
    """Screen to display detailed information about a work package."""

    CSS = """
    WorkPackageDetailsScreen {
        align: center middle;
    }

    #header {
        height: 3;
        background: $surface;
        padding: 1;
        border-bottom: solid $primary;
    }

    #header_title {
        text-style: bold;
    }

    #details_container {
        padding: 2;
        width: 100%;
        height: 100%;
        overflow-y: auto;
    }

    .detail-row {
        height: auto;
        margin-bottom: 1;
    }

    .detail-label {
        text-style: bold;
        color: $text-muted;
        width: 15;
    }

    .detail-value {
        color: $text;
    }

    #wp_description {
        height: auto;
        max-height: 10;
        overflow-y: auto;
        margin-bottom: 2;
        padding: 1;
        background: $panel;
        border: tall $panel-lighten-1;
    }

    #progress_bar {
        height: 1;
        width: 100%;
        margin-top: 1;
    }

    .status-badge {
        text-style: bold;
    }

    .meta-row {
        margin-top: 1;
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def __init__(self, work_package: WorkPackage):
        """Initialize the work package details screen."""
        super().__init__()
        self.work_package = work_package

    def compose(self) -> ComposeResult:
        """Compose the work package details screen layout."""
        with Container():
            # Header
            with Horizontal(id="header"):
                yield Label(
                    f"Work Package #{self.work_package.id} - {self.work_package.subject}",
                    id="header_title",
                )

            # Details container
            with Vertical(id="details_container"):
                # ID and Subject
                with Horizontal(classes="detail-row"):
                    yield Label("ID:", classes="detail-label")
                    yield Label(
                        str(self.work_package.id), id="wp_id", classes="detail-value"
                    )

                with Horizontal(classes="detail-row"):
                    yield Label("Subject:", classes="detail-label")
                    yield Label(
                        self.work_package.subject,
                        id="wp_subject",
                        classes="detail-value",
                    )

                # Description
                yield Label("Description:", classes="detail-label")
                description = self.work_package.description or "No description"
                yield Static(description, id="wp_description")

                # Status, Type, Priority in one row
                with Horizontal(classes="meta-row"):
                    yield Label("Status:", classes="detail-label")
                    status_text = (
                        self.work_package.status.name
                        if self.work_package.status
                        else "N/A"
                    )
                    yield Label(
                        status_text, id="wp_status", classes="detail-value status-badge"
                    )

                    yield Label("Type:", classes="detail-label")
                    type_text = (
                        self.work_package.type.name if self.work_package.type else "N/A"
                    )
                    yield Label(type_text, id="wp_type", classes="detail-value")

                    yield Label("Priority:", classes="detail-label")
                    priority_text = (
                        self.work_package.priority.name
                        if self.work_package.priority
                        else "N/A"
                    )
                    yield Label(priority_text, id="wp_priority", classes="detail-value")

                # Assignee and Author
                with Horizontal(classes="detail-row"):
                    yield Label("Assignee:", classes="detail-label")
                    assignee_text = (
                        self.work_package.assignee.name
                        if self.work_package.assignee
                        else "Unassigned"
                    )
                    yield Label(assignee_text, id="wp_assignee", classes="detail-value")

                    yield Label("Author:", classes="detail-label")
                    author_text = (
                        self.work_package.author.name
                        if self.work_package.author
                        else "N/A"
                    )
                    yield Label(author_text, id="wp_author", classes="detail-value")

                # Timeline
                with Horizontal(classes="detail-row"):
                    yield Label("Timeline:", classes="detail-label")
                    dates_info = []
                    if self.work_package.start_date:
                        dates_info.append(f"Start: {self.work_package.start_date}")
                    if self.work_package.due_date:
                        dates_info.append(f"Due: {self.work_package.due_date}")
                    if self.work_package.estimated_hours:
                        dates_info.append(
                            f"Estimated: {self.work_package.estimated_hours}h"
                        )
                    yield Label(
                        " | ".join(dates_info) if dates_info else "No timeline set",
                        id="wp_dates",
                        classes="detail-value",
                    )

                # Progress
                with Horizontal(classes="detail-row", id="progress_container"):
                    yield Label("Progress:", classes="detail-label")
                    yield Label(
                        f"{self.work_package.percentage_done or 0}%",
                        id="wp_progress",
                        classes="detail-value",
                    )

                yield ProgressBar(
                    total=100,
                    id="progress_bar",
                )

    async def on_mount(self) -> None:
        """Set initial progress when screen is mounted."""
        progress_bar = self.query_one("#progress_bar", ProgressBar)
        progress_bar.update(progress=self.work_package.percentage_done or 0)

    async def action_go_back(self) -> None:
        """Go back to the work packages list."""
        self.app.pop_screen()
