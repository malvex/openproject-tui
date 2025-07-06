"""Work package details panel widget."""

from typing import Optional

from rich.text import Text

from textual.app import ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Static, Markdown
from textual.reactive import reactive

from ..models import WorkPackage


class WorkPackagePanel(Container):
    """A panel widget to display work package details."""

    DEFAULT_CSS = """
    WorkPackagePanel {
        border: solid $primary;
        padding: 1;
        height: 100%;
    }

    #panel_header {
        margin-bottom: 1;
    }

    #panel_details {
        margin-bottom: 1;
    }

    #panel_description {
        height: auto;
    }
    """

    work_package: reactive[Optional[WorkPackage]] = reactive(None)

    def compose(self) -> ComposeResult:
        """Compose the panel layout."""
        with VerticalScroll():
            yield Static("Select a work package to view details", id="panel_header")
            yield Static("", id="panel_details")
            yield Markdown("", id="panel_description")

    def watch_work_package(self, work_package: Optional[WorkPackage]) -> None:
        """Handle work package changes."""
        if work_package is None:
            self.hide_details()
        else:
            self.show_details(work_package)

    def hide_details(self) -> None:
        """Hide work package details and show empty state."""
        header = self.query_one("#panel_header", Static)
        header.update("Select a work package to view details")
        self.query_one("#panel_details", Static).update("")
        self.query_one("#panel_description", Markdown).update("")

    def show_details(self, work_package: WorkPackage) -> None:
        """Show work package details."""
        self._update_header(work_package)
        self._update_details(work_package)
        self._update_description(work_package)

    def _update_header(self, work_package: WorkPackage) -> None:
        """Update the header with work package title."""
        header_content = Text()

        if work_package.type:
            header_content.append(work_package.type.name, style="bold cyan")
            header_content.append(" ")

        header_content.append(f"#{work_package.id}", style="bold bright_white")

        if work_package.status:
            header_content.append(" - ")
            header_content.append(
                f" {work_package.status.name} ",
                style=self._get_status_style(work_package.status.name),
            )

        header_content.append(" - ")
        header_content.append(work_package.subject, style="bold")

        self.query_one("#panel_header", Static).update(header_content)

    def _get_status_style(self, status_name: str) -> str:
        """Get the style for a status based on its name."""
        status_lower = status_name.lower()
        if "new" in status_lower:
            return "bold on blue"
        elif "progress" in status_lower:
            return "bold black on yellow"
        elif "closed" in status_lower or "done" in status_lower:
            return "bold on green"
        else:
            return "bold on cyan"

    def _update_details(self, work_package: WorkPackage) -> None:
        """Update the details section with work package metadata."""
        details_content = Text()

        details_content.append("─" * 40, style="dim")
        details_content.append("\n\n")

        self._add_priority(details_content, work_package)
        self._add_assignee(details_content, work_package)
        self._add_author(details_content, work_package)
        self._add_dates(details_content, work_package)
        self._add_progress(details_content, work_package)
        self._add_timestamps(details_content, work_package)

        self.query_one("#panel_details", Static).update(details_content)

    def _add_priority(self, content: Text, work_package: WorkPackage) -> None:
        """Add priority information to content."""
        if work_package.priority:
            content.append("Priority: ", style="bold dim")
            priority_style = self._get_priority_style(work_package.priority.name)
            content.append(work_package.priority.name, style=priority_style)
            content.append("\n")

    def _get_priority_style(self, priority_name: str) -> str:
        """Get style for priority based on its name."""
        priority_lower = priority_name.lower()
        if "high" in priority_lower:
            return "bold red"
        elif "low" in priority_lower:
            return "dim"
        return ""

    def _add_assignee(self, content: Text, work_package: WorkPackage) -> None:
        """Add assignee information to content."""
        content.append("Assignee: ", style="bold dim")
        if work_package.assignee:
            content.append(work_package.assignee.name)
        else:
            content.append("Unassigned", style="dim italic")
        content.append("\n")

    def _add_author(self, content: Text, work_package: WorkPackage) -> None:
        """Add author information to content."""
        if work_package.author:
            content.append("Author: ", style="bold dim")
            content.append(work_package.author.name)
            content.append("\n")

    def _add_dates(self, content: Text, work_package: WorkPackage) -> None:
        """Add date information to content."""
        if work_package.start_date:
            content.append("Start Date: ", style="bold dim")
            content.append(work_package.start_date)
            content.append("\n")

        if work_package.due_date:
            content.append("Due Date: ", style="bold dim")
            content.append(work_package.due_date)
            content.append("\n")

        if work_package.estimated_hours:
            content.append("Estimated: ", style="bold dim")
            content.append(f"{work_package.estimated_hours} hours")
            content.append("\n")

    def _add_progress(self, content: Text, work_package: WorkPackage) -> None:
        """Add progress information to content."""
        percentage = work_package.percentage_done or 0
        content.append("Progress: ", style="bold dim")
        progress_style = self._get_progress_style(percentage)
        content.append(f"{percentage}%", style=progress_style)
        content.append("\n")

    def _get_progress_style(self, percentage: int) -> str:
        """Get style for progress based on percentage."""
        if percentage >= 70:
            return "bold green"
        elif percentage >= 30:
            return "bold yellow"
        return ""

    def _add_timestamps(self, content: Text, work_package: WorkPackage) -> None:
        """Add timestamp information to content."""
        if work_package.created_at:
            content.append("Created: ", style="bold dim")
            content.append(
                work_package.created_at.strftime("%Y-%m-%d %H:%M"), style="dim"
            )
            content.append("\n")

        if work_package.updated_at:
            content.append("Updated: ", style="bold dim")
            content.append(
                work_package.updated_at.strftime("%Y-%m-%d %H:%M"), style="dim"
            )
            content.append("\n")

    def _update_description(self, work_package: WorkPackage) -> None:
        """Update the description section."""
        if work_package.description and work_package.description.strip():
            desc_md = f"---\n\n### Description\n\n{work_package.description}"
            self.query_one("#panel_description", Markdown).update(desc_md)
        else:
            self.query_one("#panel_description", Markdown).update("")
