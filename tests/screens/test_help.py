"""Tests for help screen."""

import pytest
from textual.widgets import Label

from src.app import OpenProjectApp
from src.screens.help import HelpScreen


class TestHelpScreen:
    """Test cases for HelpScreen."""

    @pytest.mark.asyncio
    async def test_help_screen_components(self):
        """Test help screen has required components."""
        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app
            screen = HelpScreen()
            await app.push_screen(screen)
            await pilot.pause()

            # Check for title
            title = screen.query_one("#help_title")
            assert title is not None
            assert "Keyboard Shortcuts" in str(title.renderable)

            # Check for shortcuts container
            shortcuts_container = screen.query_one("#shortcuts_container")
            assert shortcuts_container is not None

    @pytest.mark.asyncio
    async def test_help_screen_shows_shortcuts(self):
        """Test help screen displays keyboard shortcuts."""
        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app
            screen = HelpScreen()
            await app.push_screen(screen)
            await pilot.pause()

            # Check for specific labels
            all_labels = screen.query(Label)
            label_texts = [str(label.renderable) for label in all_labels]
            all_text = " ".join(label_texts)

            # Check for global shortcuts
            assert "ESC" in all_text
            assert "help screen" in all_text
            assert "Quit application" in all_text

            # Check for navigation shortcuts
            assert "Enter" in all_text
            assert "Refresh" in all_text

    @pytest.mark.asyncio
    async def test_help_screen_close(self):
        """Test closing help screen with Escape."""
        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app
            screen = HelpScreen()
            await app.push_screen(screen)
            await pilot.pause()

            initial_stack_size = len(app.screen_stack)

            # Press Escape to close help
            await pilot.press("escape")
            await pilot.pause()

            # Should pop the screen
            assert len(app.screen_stack) == initial_stack_size - 1

    @pytest.mark.asyncio
    async def test_help_screen_close_with_q(self):
        """Test closing help screen with q key."""
        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app
            screen = HelpScreen()
            await app.push_screen(screen)
            await pilot.pause()

            initial_stack_size = len(app.screen_stack)

            # Press q to close help
            await pilot.press("q")
            await pilot.pause()

            # Should pop the screen
            assert len(app.screen_stack) == initial_stack_size - 1
