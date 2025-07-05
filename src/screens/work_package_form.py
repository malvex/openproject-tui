"""Work package form screen for creating and editing."""

from typing import List, Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, TextArea

from ..client import OpenProjectClient
from ..config import config
from ..models import Priority, Project, Status, Type, User, WorkPackage


class WorkPackageFormScreen(ModalScreen[Optional[WorkPackage]]):
    """Modal screen for creating or editing a work package."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    CSS = """
    WorkPackageFormScreen {
        align: center middle;
    }

    #form_container {
        width: 80;
        height: 90%;
        max-height: 40;
        background: $surface;
        border: thick $primary;
        padding: 1 2;
        overflow-y: auto;
    }

    #form_title {
        text-style: bold;
        text-align: center;
        color: $primary;
        margin-bottom: 1;
    }

    .form-group {
        margin-bottom: 1;
        height: auto;
    }

    .form-label {
        margin-bottom: 0;
        color: $text;
    }

    Input, TextArea, Select {
        width: 100%;
        margin-top: 0;
    }

    TextArea {
        height: 6;
    }

    #buttons {
        margin-top: 2;
        align: center middle;
    }

    #buttons Button {
        margin: 0 1;
    }

    #error_message {
        color: $error;
        text-align: center;
        margin-top: 1;
        display: none;
    }

    #loading_message {
        text-align: center;
        margin-top: 1;
        display: none;
    }
    """

    def __init__(
        self,
        project: Project,
        work_package: Optional[WorkPackage] = None,
    ):
        """Initialize the form screen.

        Args:
            project: The project to create the work package in
            work_package: Optional work package to edit (None for create)
        """
        super().__init__()
        self.project = project
        self.work_package = work_package
        self.is_edit = work_package is not None
        self.client = OpenProjectClient(api_url=config.api_url, api_key=config.api_key)

        # Available options for selects
        self.types: List[Type] = []
        self.statuses: List[Status] = []
        self.priorities: List[Priority] = []
        self.users: List[User] = []

    def compose(self) -> ComposeResult:
        """Compose the form layout."""
        title = (
            f"Edit Work Package #{self.work_package.id}"
            if self.is_edit
            else "New Work Package"
        )

        with Container(id="form_container"):
            yield Label(title, id="form_title")

            with VerticalScroll():
                # Subject
                with Container(classes="form-group"):
                    yield Label("Subject *", classes="form-label")
                    yield Input(
                        value=self.work_package.subject if self.work_package else "",
                        placeholder="Enter work package subject...",
                        id="subject_input",
                    )

                # Type
                with Container(classes="form-group"):
                    yield Label("Type *", classes="form-label")
                    yield Select(
                        options=[],
                        id="type_select",
                        prompt="Select type...",
                    )

                # Description
                with Container(classes="form-group"):
                    yield Label("Description", classes="form-label")
                    yield TextArea(
                        self.work_package.description if self.work_package else "",
                        id="description_input",
                    )

                # Status
                with Container(classes="form-group"):
                    yield Label("Status", classes="form-label")
                    yield Select(
                        options=[],
                        id="status_select",
                        prompt="Select status...",
                        disabled=not self.is_edit,  # Disabled until type is selected for new
                    )

                # Priority
                with Container(classes="form-group"):
                    yield Label("Priority", classes="form-label")
                    yield Select(
                        options=[],
                        id="priority_select",
                        prompt="Select priority...",
                    )

                # Assignee
                with Container(classes="form-group"):
                    yield Label("Assignee", classes="form-label")
                    yield Select(
                        options=[],
                        id="assignee_select",
                        prompt="Select assignee...",
                        allow_blank=True,
                    )

                # Buttons
                with Horizontal(id="buttons"):
                    yield Button("Save", variant="primary", id="save_button")
                    yield Button("Cancel", variant="default", id="cancel_button")

                # Messages
                yield Label("", id="error_message")
                yield Label("Loading options...", id="loading_message")

    async def on_mount(self) -> None:
        """Load form options when mounted."""
        await self.load_options()
        # Focus on the subject input
        self.query_one("#subject_input", Input).focus()

    async def load_options(self) -> None:
        """Load available options for select fields."""
        loading_msg = self.query_one("#loading_message", Label)
        error_msg = self.query_one("#error_message", Label)

        loading_msg.display = True
        error_msg.display = False

        try:
            # Load all required data in parallel where possible
            await self._load_form_data()

            # Update UI with loaded data
            self._populate_select_options()

            # Set current values for edit mode
            if self.is_edit:
                self._set_current_values()

            loading_msg.display = False

        except Exception as e:
            loading_msg.display = False
            error_msg.display = True
            error_msg.update(f"Error loading options: {str(e)}")
            # Log the full error for debugging
            import traceback

            traceback.print_exc()

    async def _load_form_data(self) -> None:
        """Load all form data from API."""
        # Load types
        self.types = await self.client.get_types(project_id=self.project.id)
        self._ensure_current_type_in_list()

        # Load priorities
        self.priorities = await self.client.get_priorities()

        # Load users
        await self._load_users()

        # Load statuses
        await self._load_statuses()

    def _ensure_current_type_in_list(self) -> None:
        """Ensure current work package type is in the types list."""
        if self.is_edit and self.work_package and self.work_package.type:
            current_type_id = self.work_package.type.id
            if not any(t.id == current_type_id for t in self.types):
                self.types.insert(0, self.work_package.type)

    async def _load_users(self) -> None:
        """Load project members."""
        try:
            self.users = await self.client.get_project_members(self.project.id)
        except Exception as e:
            print(f"Warning: Could not load project members: {e}")
            self.users = []

    async def _load_statuses(self) -> None:
        """Load available statuses based on form mode."""
        if self.is_edit and self.work_package:
            try:
                self.statuses = await self.client.get_available_status_transitions(
                    self.work_package.id
                )
            except Exception:
                self.statuses = await self.client.get_statuses()
        else:
            # For new work packages, statuses will be loaded when type is selected
            self.statuses = []

    def _populate_select_options(self) -> None:
        """Populate all select widgets with their options."""
        # Types
        type_select = self.query_one("#type_select", Select)
        type_select.set_options([(t.name, t.id) for t in self.types])

        # Statuses
        if self.statuses:
            status_select = self.query_one("#status_select", Select)
            status_select.set_options([(s.name, s.id) for s in self.statuses])

        # Priorities
        priority_select = self.query_one("#priority_select", Select)
        priority_select.set_options([(p.name, p.id) for p in self.priorities])

        # Assignees
        assignee_select = self.query_one("#assignee_select", Select)
        assignee_options = [("Unassigned", 0)] + [(u.name, u.id) for u in self.users]
        assignee_select.set_options(assignee_options)

    def _set_current_values(self) -> None:
        """Set current values for edit mode."""
        if not self.work_package:
            return

        # Type
        if self.work_package.type and self._has_option(
            self.types, self.work_package.type.id
        ):
            self.query_one("#type_select", Select).value = self.work_package.type.id

        # Status
        if self.work_package.status and self._has_option(
            self.statuses, self.work_package.status.id
        ):
            self.query_one("#status_select", Select).value = self.work_package.status.id

        # Priority
        if self.work_package.priority and self._has_option(
            self.priorities, self.work_package.priority.id
        ):
            self.query_one(
                "#priority_select", Select
            ).value = self.work_package.priority.id

        # Assignee
        if self.work_package.assignee:
            assignee_id = self.work_package.assignee.id
            if assignee_id == 0 or self._has_option(self.users, assignee_id):
                self.query_one("#assignee_select", Select).value = assignee_id

    def _has_option(self, options: List, option_id: int) -> bool:
        """Check if an option exists in the list."""
        return any(opt.id == option_id for opt in options)

    @on(Select.Changed, "#type_select")
    async def on_type_changed(self, event: Select.Changed) -> None:
        """Handle type selection change to load appropriate statuses."""
        if event.value:
            try:
                if self.is_edit and self.work_package:
                    # For edit mode, get allowed statuses when type changes
                    self.statuses = await self.client.get_available_status_transitions(
                        self.work_package.id,
                        type_id=event.value,
                        lock_version=self.work_package.lock_version,
                    )
                else:
                    # For new work packages
                    self.statuses = await self.client.get_available_statuses_for_new(
                        self.project.id, event.value
                    )

                # Update status select options
                status_select = self.query_one("#status_select", Select)
                status_select.set_options(
                    [(status.name, status.id) for status in self.statuses]
                )

                # Enable status select (for new work packages)
                if not self.is_edit:
                    status_select.disabled = False

                # Handle status selection
                if self.statuses:
                    # If current status is still valid, keep it selected
                    if self.is_edit and self.work_package and self.work_package.status:
                        current_status_id = self.work_package.status.id
                        if any(s.id == current_status_id for s in self.statuses):
                            status_select.value = current_status_id
                        else:
                            # Current status not valid anymore, select first available
                            status_select.value = self.statuses[0].id
                    else:
                        # Select first status for new work packages
                        status_select.value = self.statuses[0].id

            except Exception as e:
                print(f"Could not load statuses for type: {e}")

    @on(Button.Pressed, "#save_button")
    async def on_save(self) -> None:
        """Handle save button press."""
        error_msg = self.query_one("#error_message", Label)
        error_msg.display = False

        # Get form values
        subject = self.query_one("#subject_input", Input).value.strip()
        type_id = self.query_one("#type_select", Select).value
        description = self.query_one("#description_input", TextArea).text
        priority_id = self.query_one("#priority_select", Select).value
        assignee_id = self.query_one("#assignee_select", Select).value

        # Validate required fields
        if not subject:
            error_msg.display = True
            error_msg.update("Subject is required")
            return

        if not type_id:
            error_msg.display = True
            error_msg.update("Type is required")
            return

        try:
            status_id = self.query_one("#status_select", Select).value

            if self.is_edit and self.work_package:
                # Update existing work package
                updated_wp = await self.client.update_work_package(
                    work_package_id=self.work_package.id,
                    subject=subject,
                    description=description if description else None,
                    assignee_id=assignee_id if assignee_id else None,
                    status_id=status_id if status_id else None,
                    priority_id=priority_id if priority_id else None,
                    lock_version=self.work_package.lock_version,
                )
                self.dismiss(updated_wp)
            else:
                # Create new work package
                new_wp = await self.client.create_work_package(
                    project_id=self.project.id,
                    subject=subject,
                    type_id=type_id,
                    description=description if description else None,
                    assignee_id=assignee_id if assignee_id else None,
                    status_id=status_id if status_id else None,
                    priority_id=priority_id if priority_id else None,
                )
                self.dismiss(new_wp)

        except Exception as e:
            error_msg.display = True
            error_msg.update(f"Error saving: {str(e)}")

    @on(Button.Pressed, "#cancel_button")
    async def on_cancel(self) -> None:
        """Handle cancel button press."""
        self.dismiss(None)

    async def action_cancel(self) -> None:
        """Handle ESC key to cancel the form."""
        self.dismiss(None)

    async def on_unmount(self) -> None:
        """Clean up when screen is unmounted."""
        await self.client.close()
