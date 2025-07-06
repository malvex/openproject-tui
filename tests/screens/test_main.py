"""Tests for main screen."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.app import OpenProjectApp
from src.screens.main import MainScreen
from src.models import Project


class TestMainScreen:
    """Test cases for MainScreen."""

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
        ]

    @pytest.mark.asyncio
    async def test_main_screen_components(self):
        """Test main screen has required components."""
        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app

            with patch("src.screens.main.OpenProjectClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client.get_projects = AsyncMock(return_value=[])
                mock_client.close = AsyncMock()
                mock_client_class.return_value = mock_client

                screen = MainScreen()
                await app.push_screen(screen)
                await pilot.pause()

                # Check for Header widget
                from textual.widgets import Header

                assert screen.query_one(Header) is not None

                # Check for projects table
                table = screen.query_one("#projects_table")
                assert table is not None

                # Check table has correct columns
                assert len(table.columns) == 5  # ID, Identifier, Name, Status, Public

    @pytest.mark.asyncio
    async def test_main_screen_loads_projects(self, mock_projects):
        """Test main screen loads projects on mount."""
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

                # Verify projects were loaded
                table = screen.query_one("#projects_table")
                assert table.row_count == len(mock_projects)

    @pytest.mark.asyncio
    async def test_main_screen_project_selection(self, mock_projects):
        """Test selecting a project navigates to work packages."""
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

                # Select first project (Enter key)
                table = screen.query_one("#projects_table")
                table.focus()

                # Mock the work packages screen push
                with patch.object(app, "push_screen"):
                    await pilot.press("enter")
                    await pilot.pause()

                    # Note: The actual navigation will be implemented
                    # when we create the work packages screen

    @pytest.mark.asyncio
    async def test_main_screen_error_handling(self):
        """Test error handling when loading projects fails."""
        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app

            with patch("src.screens.main.OpenProjectClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client.get_projects = AsyncMock(
                    side_effect=Exception("Connection failed")
                )
                mock_client.close = AsyncMock()
                mock_client_class.return_value = mock_client

                screen = MainScreen()
                await app.push_screen(screen)
                await pilot.pause()

                # Check for error message
                error_label = screen.query_one("#error")
                assert error_label is not None
                assert "Error loading projects" in str(error_label.renderable)
