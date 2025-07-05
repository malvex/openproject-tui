"""Tests for work package details screen."""

import pytest

from src.app import OpenProjectApp
from src.screens.work_package_details import WorkPackageDetailsScreen
from src.models import WorkPackage, Status, Type, Priority, User, Project


class TestWorkPackageDetailsScreen:
    """Test cases for WorkPackageDetailsScreen."""

    @pytest.fixture
    def mock_work_package(self):
        """Create a mock work package with full details."""
        return WorkPackage(
            id=1,
            subject="Fix login bug",
            description="Login fails with special characters in password. Users report that when they use characters like @, #, or $ in their passwords, the login process fails with a 401 error.",
            start_date="2024-01-01",
            due_date="2024-01-15",
            estimated_hours=8.0,
            percentage_done=50,
            created_at="2024-01-01T10:00:00Z",
            updated_at="2024-01-02T14:30:00Z",
            status=Status(id=1, name="In Progress", color="#0066CC"),
            type=Type(id=2, name="Bug", color="#CC0000"),
            priority=Priority(id=8, name="High"),
            project=Project(
                id=1,
                identifier="demo-project",
                name="Demo Project",
                active=True,
                public=False,
            ),
            author=User(id=1, name="John Doe", email="john@example.com"),
            assignee=User(id=2, name="Jane Smith", email="jane@example.com"),
        )

    @pytest.mark.asyncio
    async def test_work_package_details_screen_components(self, mock_work_package):
        """Test work package details screen has required components."""
        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app
            screen = WorkPackageDetailsScreen(mock_work_package)
            await app.push_screen(screen)
            await pilot.pause()

            # Check for details container
            details_container = screen.query_one("#details_container")
            assert details_container is not None

            # Check for all detail fields
            assert screen.query_one("#wp_id") is not None
            assert screen.query_one("#subject_header") is not None
            assert screen.query_one("#wp_description") is not None
            assert screen.query_one("#wp_status") is not None
            assert screen.query_one("#wp_type") is not None
            assert screen.query_one("#wp_assignee") is not None
            assert screen.query_one("#wp_author") is not None
            assert screen.query_one("#wp_dates") is not None
            assert screen.query_one("#wp_progress") is not None

    @pytest.mark.asyncio
    async def test_work_package_details_displays_data(self, mock_work_package):
        """Test work package details are displayed correctly."""
        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app
            screen = WorkPackageDetailsScreen(mock_work_package)
            await app.push_screen(screen)
            await pilot.pause()

            # Check that data is displayed
            subject_label = screen.query_one("#subject_header")
            assert mock_work_package.subject in str(subject_label.renderable)

            status_label = screen.query_one("#wp_status")
            assert "In Progress" in str(status_label.renderable)

            assignee_label = screen.query_one("#wp_assignee")
            assert "Jane Smith" in str(assignee_label.renderable)

    @pytest.mark.asyncio
    async def test_work_package_details_no_description(self):
        """Test work package details when description is None."""
        wp = WorkPackage(
            id=2,
            subject="Simple task",
            description=None,
            status=Status(id=1, name="New", color="#0066CC"),
            type=Type(id=1, name="Task", color="#0066CC"),
            priority=Priority(id=7, name="Normal"),
            project=Project(
                id=1,
                identifier="demo-project",
                name="Demo Project",
                active=True,
                public=False,
            ),
            author=User(id=1, name="John Doe", email="john@example.com"),
        )

        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app
            screen = WorkPackageDetailsScreen(wp)
            await app.push_screen(screen)
            await pilot.pause()

            # Check that empty description is handled
            description_label = screen.query_one("#wp_description")
            assert "No description" in str(description_label.renderable)

    @pytest.mark.asyncio
    async def test_work_package_details_no_assignee(self):
        """Test work package details when assignee is None."""
        wp = WorkPackage(
            id=3,
            subject="Unassigned task",
            status=Status(id=1, name="New", color="#0066CC"),
            type=Type(id=1, name="Task", color="#0066CC"),
            priority=Priority(id=7, name="Normal"),
            project=Project(
                id=1,
                identifier="demo-project",
                name="Demo Project",
                active=True,
                public=False,
            ),
            author=User(id=1, name="John Doe", email="john@example.com"),
            assignee=None,
        )

        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app
            screen = WorkPackageDetailsScreen(wp)
            await app.push_screen(screen)
            await pilot.pause()

            # Check that unassigned is handled
            assignee_label = screen.query_one("#wp_assignee")
            assert "Unassigned" in str(assignee_label.renderable)

    @pytest.mark.asyncio
    async def test_back_navigation(self, mock_work_package):
        """Test pressing Escape goes back to work packages list."""
        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app
            screen = WorkPackageDetailsScreen(mock_work_package)
            await app.push_screen(screen)
            await pilot.pause()

            initial_stack_size = len(app.screen_stack)

            # Press Escape
            await pilot.press("escape")
            await pilot.pause()

            # Should pop the screen
            assert len(app.screen_stack) == initial_stack_size - 1

    @pytest.mark.asyncio
    async def test_work_package_details_progress_bar(self, mock_work_package):
        """Test progress bar displays correctly."""
        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app
            screen = WorkPackageDetailsScreen(mock_work_package)
            await app.push_screen(screen)
            await pilot.pause()

            # Check progress bar exists and shows correct percentage
            progress_bar = screen.query_one("#progress_bar")
            assert progress_bar is not None
            assert progress_bar.percentage == 0.5  # 50% as decimal
