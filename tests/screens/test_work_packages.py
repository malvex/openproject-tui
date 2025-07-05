"""Tests for work packages screen."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.app import OpenProjectApp
from src.screens.work_packages import WorkPackagesScreen
from src.models import Project, WorkPackage, Status, Type, Priority, User


class TestWorkPackagesScreen:
    """Test cases for WorkPackagesScreen."""

    @pytest.fixture
    def mock_project(self):
        """Create a mock project."""
        return Project(
            id=1,
            identifier="demo-project",
            name="Demo Project",
            active=True,
            public=False,
            description="A demo project",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-02T00:00:00Z",
        )

    @pytest.fixture
    def mock_work_packages(self):
        """Create mock work packages."""
        return [
            WorkPackage(
                id=1,
                subject="Fix login bug",
                description="Login fails with special characters",
                start_date="2024-01-01",
                due_date="2024-01-15",
                estimated_time="PT8H",
                percentage_done=50,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-02T00:00:00Z",
                status=Status(id=1, name="New", color="#0066CC"),
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
            ),
            WorkPackage(
                id=2,
                subject="Add new feature",
                description="Implement user preferences",
                start_date="2024-01-10",
                due_date="2024-01-20",
                estimated_time="PT16H",
                percentage_done=0,
                created_at="2024-01-10T00:00:00Z",
                updated_at="2024-01-10T00:00:00Z",
                status=Status(id=2, name="In Progress", color="#00CC00"),
                type=Type(id=1, name="Feature", color="#0066CC"),
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
            ),
        ]

    @pytest.mark.asyncio
    async def test_work_packages_screen_components(self, mock_project):
        """Test work packages screen has required components."""
        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app
            screen = WorkPackagesScreen(mock_project)
            await app.push_screen(screen)
            await pilot.pause()

            # Check for header with project name
            header = screen.query_one("#header")
            assert header is not None
            project_label = screen.query_one("#project_name")
            assert project_label is not None
            assert mock_project.name in project_label.renderable

            # Check for work packages table
            table = screen.query_one("#work_packages_table")
            assert table is not None

            # Check for loading indicator
            loading = screen.query_one("#loading")
            assert loading is not None

    @pytest.mark.asyncio
    async def test_work_packages_screen_loads_data(
        self, mock_project, mock_work_packages
    ):
        """Test work packages screen loads data on mount."""
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

                screen = WorkPackagesScreen(mock_project)
                await app.push_screen(screen)
                await pilot.pause()

                # Verify client was called with correct project ID
                mock_client.get_work_packages.assert_called_once_with(
                    project_id=mock_project.id
                )

                # Check table has correct columns
                table = screen.query_one("#work_packages_table")
                assert (
                    len(table.columns) >= 6
                )  # ID, Subject, Status, Type, Priority, Assignee

    @pytest.mark.asyncio
    async def test_work_packages_table_displays_data(
        self, mock_project, mock_work_packages
    ):
        """Test work packages are displayed in the table."""
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

                screen = WorkPackagesScreen(mock_project)
                await app.push_screen(screen)
                await pilot.pause()

                # Check table has rows
                table = screen.query_one("#work_packages_table")
                assert table.row_count == len(mock_work_packages)

    @pytest.mark.asyncio
    async def test_work_packages_empty_state(self, mock_project):
        """Test empty state when no work packages."""
        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app

            with patch(
                "src.screens.work_packages.OpenProjectClient"
            ) as mock_client_class:
                mock_client = MagicMock()
                mock_client.get_work_packages = AsyncMock(return_value=[])
                mock_client.close = AsyncMock()
                mock_client_class.return_value = mock_client

                screen = WorkPackagesScreen(mock_project)
                await app.push_screen(screen)
                await pilot.pause()

                # Check for empty message
                empty_label = screen.query_one("#empty_message")
                assert empty_label is not None
                assert "No work packages" in str(empty_label.renderable)

    @pytest.mark.asyncio
    async def test_work_packages_error_handling(self, mock_project):
        """Test error handling when loading fails."""
        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app

            with patch(
                "src.screens.work_packages.OpenProjectClient"
            ) as mock_client_class:
                mock_client = MagicMock()
                mock_client.get_work_packages = AsyncMock(
                    side_effect=Exception("API Error")
                )
                mock_client_class.return_value = mock_client

                screen = WorkPackagesScreen(mock_project)
                await app.push_screen(screen)
                await pilot.pause()

                # Check for error message
                error_label = screen.query_one("#error")
                assert error_label is not None
                assert "Error loading work packages" in str(error_label.renderable)

    @pytest.mark.asyncio
    async def test_back_navigation(self, mock_project):
        """Test pressing Escape goes back to main screen."""
        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app

            with patch(
                "src.screens.work_packages.OpenProjectClient"
            ) as mock_client_class:
                mock_client = MagicMock()
                mock_client.get_work_packages = AsyncMock(return_value=[])
                mock_client.close = AsyncMock()
                mock_client_class.return_value = mock_client

                screen = WorkPackagesScreen(mock_project)
                await app.push_screen(screen)
                await pilot.pause()

                # Press Escape
                await pilot.press("escape")
                await pilot.pause()

                # Should pop the screen
                assert len(app.screen_stack) < 2
