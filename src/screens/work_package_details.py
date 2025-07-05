"""Work package details screen for OpenProject TUI."""

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Label, ProgressBar, Static

from ..models import Project, WorkPackage


class WorkPackageDetailsScreen(Screen):
    """Screen to display detailed information about a work package."""

    CSS = """
    #details_container {
        padding: 1 2;
        overflow-y: auto;
    }

    #header_section {
        border-bottom: solid $primary;
        padding-bottom: 1;
        margin-bottom: 2;
    }

    #wp_id {
        color: $text-muted;
    }

    #subject_header {
        text-style: bold;
        color: $text;
        margin-top: 1;
    }

    #wp_description {
        padding: 1;
        margin: 1 0;
        background: $panel;
        border: tall $panel-lighten-1;
    }

    .section {
        margin-bottom: 2;
    }

    .section-title {
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }

    .field-row {
        height: 1;
        margin-bottom: 1;
    }

    .field-label {
        width: 12;
        color: $text-muted;
    }

    .field-value {
        color: $text;
    }

    #progress_bar {
        margin-top: 1;
    }
    """

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("e", "edit", "Edit"),
    ]

    def __init__(self, work_package: WorkPackage, project: Optional[Project] = None):
        """Initialize the work package details screen."""
        super().__init__()
        self.work_package = work_package
        # Use the provided project or the one from the work package
        self.project = project or work_package.project

    def compose(self) -> ComposeResult:
        """Compose the work package details screen layout."""
        with Vertical(id="details_container"):
            # Header section
            with Container(id="header_section"):
                yield Label(f"Work Package #{self.work_package.id}", id="wp_id")
                yield Label(self.work_package.subject, id="subject_header")

            # Description
            if self.work_package.description:
                yield Static(self.work_package.description, id="wp_description")

            # Details section
            with Container(classes="section"):
                yield Label("Details", classes="section-title")

                # Status
                status_text = (
                    self.work_package.status.name if self.work_package.status else "N/A"
                )
                with Horizontal(classes="field-row"):
                    yield Label("Status:", classes="field-label")
                    yield Label(status_text, id="wp_status", classes="field-value")

                # Type
                type_text = (
                    self.work_package.type.name if self.work_package.type else "N/A"
                )
                with Horizontal(classes="field-row"):
                    yield Label("Type:", classes="field-label")
                    yield Label(type_text, id="wp_type", classes="field-value")

                # Priority
                priority_text = (
                    self.work_package.priority.name
                    if self.work_package.priority
                    else "N/A"
                )
                with Horizontal(classes="field-row"):
                    yield Label("Priority:", classes="field-label")
                    yield Label(priority_text, id="wp_priority", classes="field-value")

            # People section
            with Container(classes="section"):
                yield Label("People", classes="section-title")

                # Assignee
                assignee_text = (
                    self.work_package.assignee.name
                    if self.work_package.assignee
                    else "Unassigned"
                )
                with Horizontal(classes="field-row"):
                    yield Label("Assignee:", classes="field-label")
                    yield Label(assignee_text, id="wp_assignee", classes="field-value")

                # Author
                author_text = (
                    self.work_package.author.name
                    if self.work_package.author
                    else "Unknown"
                )
                with Horizontal(classes="field-row"):
                    yield Label("Author:", classes="field-label")
                    yield Label(author_text, id="wp_author", classes="field-value")

            # Timeline section
            if any(
                [
                    self.work_package.start_date,
                    self.work_package.due_date,
                    self.work_package.estimated_hours,
                ]
            ):
                with Container(classes="section"):
                    yield Label("Timeline", classes="section-title")

                    if self.work_package.start_date:
                        with Horizontal(classes="field-row"):
                            yield Label("Start Date:", classes="field-label")
                            yield Label(
                                self.work_package.start_date, classes="field-value"
                            )

                    if self.work_package.due_date:
                        with Horizontal(classes="field-row"):
                            yield Label("Due Date:", classes="field-label")
                            yield Label(
                                self.work_package.due_date, classes="field-value"
                            )

                    if self.work_package.estimated_hours:
                        with Horizontal(classes="field-row"):
                            yield Label("Estimated:", classes="field-label")
                            yield Label(
                                f"{self.work_package.estimated_hours} hours",
                                classes="field-value",
                            )

                    # Combined dates for test compatibility
                    dates_parts = []
                    if self.work_package.start_date:
                        dates_parts.append(f"Start: {self.work_package.start_date}")
                    if self.work_package.due_date:
                        dates_parts.append(f"Due: {self.work_package.due_date}")
                    if self.work_package.estimated_hours:
                        dates_parts.append(f"Est: {self.work_package.estimated_hours}h")
                    yield Label(
                        " • ".join(dates_parts),
                        id="wp_dates",
                        classes="field-value",
                        disabled=True,
                    )

            # Progress section
            with Container(classes="section"):
                yield Label("Progress", classes="section-title")
                percentage = self.work_package.percentage_done or 0
                with Horizontal(classes="field-row"):
                    yield Label("Completion:", classes="field-label")
                    yield Label(
                        f"{percentage}%", id="wp_progress", classes="field-value"
                    )
                yield ProgressBar(total=100, id="progress_bar")

    async def on_mount(self) -> None:
        """Set initial progress when screen is mounted."""
        progress_bar = self.query_one("#progress_bar", ProgressBar)
        progress_bar.update(progress=self.work_package.percentage_done or 0)

    async def action_go_back(self) -> None:
        """Go back to the work packages list."""
        self.app.pop_screen()

    async def action_edit(self) -> None:
        """Edit this work package."""
        from .work_package_form import WorkPackageFormScreen

        def on_dismiss(result: Optional[WorkPackage]) -> None:
            """Handle form dismissal."""
            if result:
                # Update the current work package and refresh display
                self.work_package = result
                self.refresh()

        # Use the project we have (either from constructor or work package)
        if self.project:
            self.app.push_screen(
                WorkPackageFormScreen(self.project, self.work_package),
                on_dismiss,
            )
        else:
            # If no project available, show error
            self.notify(
                "Cannot edit: Project information not available", severity="error"
            )
