"""Work package details screen for OpenProject TUI."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Label, ProgressBar, Static

from ..models import WorkPackage


class WorkPackageDetailsScreen(Screen):
    """Screen to display detailed information about a work package."""

    CSS = """
    #details_container {
        padding: 1 2;
        overflow-y: auto;
    }

    Label {
        height: 1;
    }

    #subject_header {
        text-style: bold;
        color: $text;
        margin-bottom: 1;
    }

    #wp_description {
        margin: 1 0 2 0;
        color: $text-muted;
    }

    .info-line {
        margin-bottom: 1;
    }

    .label {
        color: $text-muted;
    }

    .value {
        color: $text;
        text-style: bold;
    }

    #progress_bar {
        margin-top: 1;
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
        with Vertical(id="details_container"):
            # Work package number and subject as header
            yield Label(f"#{self.work_package.id}", id="wp_id", classes="label")
            yield Label(self.work_package.subject, id="subject_header")

            # Description
            description = self.work_package.description or "No description provided"
            yield Static(description, id="wp_description")

            # Core info
            status_text = (
                self.work_package.status.name if self.work_package.status else "N/A"
            )
            type_text = self.work_package.type.name if self.work_package.type else "N/A"
            priority_text = (
                self.work_package.priority.name if self.work_package.priority else "N/A"
            )

            yield Label(f"Status: {status_text}", id="wp_status", classes="info-line")
            yield Label(
                f"Type: {type_text} • Priority: {priority_text}",
                id="wp_type",
                classes="info-line",
            )

            # People
            assignee_text = (
                self.work_package.assignee.name
                if self.work_package.assignee
                else "Unassigned"
            )
            author_text = (
                self.work_package.author.name if self.work_package.author else "Unknown"
            )

            yield Label(
                f"Assignee: {assignee_text}", id="wp_assignee", classes="info-line"
            )
            yield Label(f"Author: {author_text}", id="wp_author", classes="info-line")

            # Dates
            dates_parts = []
            if self.work_package.start_date:
                dates_parts.append(f"Start: {self.work_package.start_date}")
            if self.work_package.due_date:
                dates_parts.append(f"Due: {self.work_package.due_date}")
            if self.work_package.estimated_hours:
                dates_parts.append(f"Est: {self.work_package.estimated_hours}h")

            if dates_parts:
                yield Label(" • ".join(dates_parts), id="wp_dates", classes="info-line")

            # Progress
            percentage = self.work_package.percentage_done or 0
            yield Label(
                f"Progress: {percentage}%", id="wp_progress", classes="info-line"
            )
            yield ProgressBar(total=100, id="progress_bar")

    async def on_mount(self) -> None:
        """Set initial progress when screen is mounted."""
        progress_bar = self.query_one("#progress_bar", ProgressBar)
        progress_bar.update(progress=self.work_package.percentage_done or 0)

    async def action_go_back(self) -> None:
        """Go back to the work packages list."""
        self.app.pop_screen()
