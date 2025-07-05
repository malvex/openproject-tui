"""Tests for search functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from textual.widgets import Input

from src.app import OpenProjectApp
from src.screens.main import MainScreen
from src.screens.work_packages import WorkPackagesScreen
from src.models import Project, WorkPackage, Status, Type, Priority, User


class TestSearchFunctionality:
    """Test cases for search functionality in screens."""

    @pytest.fixture
    def mock_projects(self):
        """Create mock projects."""
        return [
            Project(
                id=1,
                identifier="demo-project",
                name="Demo Project",
                active=True,
                public=False,
                description="A demo project",
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-02T00:00:00Z",
            ),
            Project(
                id=2,
                identifier="test-project",
                name="Test Project",
                active=True,
                public=True,
                description="A test project",
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-02T00:00:00Z",
            ),
            Project(
                id=3,
                identifier="another-demo",
                name="Another Demo",
                active=True,
                public=False,
                description="Another demo project",
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-02T00:00:00Z",
            ),
        ]

    @pytest.mark.asyncio
    async def test_main_screen_search_toggle(self, mock_projects):
        """Test pressing / shows search input on main screen."""
        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app

            with patch("src.screens.main.OpenProjectClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client.get_projects = AsyncMock(return_value=mock_projects)
                mock_client.close = AsyncMock()
                mock_client_class.return_value = mock_client

                screen = MainScreen()
                await app.push_screen(screen)
                await pilot.pause()

                # Initially, search input should be hidden
                search_input = screen.query_one("#search_input", Input)
                assert search_input.has_class("hidden")

                # Press / to show search
                await pilot.press("/")
                await pilot.pause()

                # Search should now be visible and focused
                assert not search_input.has_class("hidden")
                assert search_input.has_focus

    @pytest.mark.asyncio
    async def test_main_screen_search_filter(self, mock_projects):
        """Test search filters projects by name."""
        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app

            with patch("src.screens.main.OpenProjectClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client.get_projects = AsyncMock(return_value=mock_projects)
                mock_client.close = AsyncMock()
                mock_client_class.return_value = mock_client

                screen = MainScreen()
                await app.push_screen(screen)
                await pilot.pause()

                # Show search
                await pilot.press("/")
                await pilot.pause()

                # Type search term
                search_input = screen.query_one("#search_input", Input)
                search_input.value = "demo"
                await pilot.pause()

                # Check that table is filtered
                table = screen.query_one("#projects_table")
                # Should show only projects with "demo" in the name
                assert table.row_count == 2  # "Demo Project" and "Another Demo"

    @pytest.mark.asyncio
    async def test_main_screen_clear_search(self, mock_projects):
        """Test clearing search with ESC."""
        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app

            with patch("src.screens.main.OpenProjectClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client.get_projects = AsyncMock(return_value=mock_projects)
                mock_client.close = AsyncMock()
                mock_client_class.return_value = mock_client

                screen = MainScreen()
                await app.push_screen(screen)
                await pilot.pause()

                # Show search and type
                await pilot.press("/")
                await pilot.pause()

                search_input = screen.query_one("#search_input", Input)
                search_input.value = "test"
                await pilot.pause()

                # Press ESC to clear and hide search
                await pilot.press("escape")
                await pilot.pause()

                # Search input should be hidden and table should show all projects
                assert search_input.has_class("hidden")
                assert search_input.value == ""

                table = screen.query_one("#projects_table")
                assert table.row_count == 3  # All projects

    @pytest.fixture
    def mock_work_packages(self):
        """Create mock work packages."""
        return [
            WorkPackage(
                id=1,
                subject="Fix login bug",
                description="Login fails with special characters",
                status=Status(id=1, name="New", color="#0066CC"),
                type=Type(id=2, name="Bug", color="#CC0000"),
                priority=Priority(id=8, name="High"),
                assignee=User(id=1, name="John Doe", email="john@example.com"),
            ),
            WorkPackage(
                id=2,
                subject="Add new feature",
                description="Implement user preferences",
                status=Status(id=2, name="In Progress", color="#00CC00"),
                type=Type(id=1, name="Feature", color="#0066CC"),
                priority=Priority(id=7, name="Normal"),
                assignee=User(id=2, name="Jane Smith", email="jane@example.com"),
            ),
            WorkPackage(
                id=3,
                subject="Fix performance issue",
                description="App is slow on large datasets",
                status=Status(id=1, name="New", color="#0066CC"),
                type=Type(id=2, name="Bug", color="#CC0000"),
                priority=Priority(id=9, name="Immediate"),
                assignee=None,
            ),
        ]

    @pytest.mark.asyncio
    async def test_work_packages_screen_search(self, mock_work_packages):
        """Test search on work packages screen."""
        project = Project(
            id=1,
            identifier="test-project",
            name="Test Project",
            active=True,
            public=False,
        )

        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app

            with patch(
                "src.screens.work_packages.OpenProjectClient"
            ) as mock_client_class:
                mock_client = MagicMock()
                mock_client.get_work_packages = AsyncMock(
                    return_value=mock_work_packages
                )
                mock_client.close = AsyncMock()
                mock_client_class.return_value = mock_client

                screen = WorkPackagesScreen(project)
                await app.push_screen(screen)
                await pilot.pause()

                # Show search
                await pilot.press("/")
                await pilot.pause()

                # Search for "fix"
                search_input = screen.query_one("#search_input", Input)
                search_input.value = "fix"
                await pilot.pause()

                # Should show work packages with "fix" in subject
                table = screen.query_one("#work_packages_table")
                assert table.row_count == 2  # Two items with "fix"
