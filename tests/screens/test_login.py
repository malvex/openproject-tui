"""Tests for screens."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.app import OpenProjectApp
from src.screens.login import LoginScreen
from src.client import AuthenticationError


class TestLoginScreen:
    """Test cases for LoginScreen."""

    @pytest.mark.asyncio
    async def test_login_screen_components(self):
        """Test login screen has required components."""
        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app
            login_screen = LoginScreen()
            await app.push_screen(login_screen)
            await pilot.pause()  # Wait for screen to mount

            # Check for required inputs
            api_url_input = login_screen.query_one("#api_url")
            assert api_url_input is not None
            assert api_url_input.placeholder == "https://openproject.example.com"

            api_key_input = login_screen.query_one("#api_key")
            assert api_key_input is not None
            assert api_key_input.password is True
            assert api_key_input.placeholder == "Your API key"

            # Check for login button
            login_button = login_screen.query_one("#login_button")
            assert login_button is not None
            assert login_button.label == "Login"

    @pytest.mark.asyncio
    async def test_login_success(self):
        """Test successful login."""
        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app
            login_screen = LoginScreen()
            await app.push_screen(login_screen)
            await pilot.pause()

            # Fill in the form
            api_url_input = login_screen.query_one("#api_url")
            api_key_input = login_screen.query_one("#api_key")

            api_url_input.value = "https://test.openproject.org"
            api_key_input.value = "test_api_key"

            # Mock successful connection test
            with patch("src.screens.login.OpenProjectClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client.test_connection = AsyncMock(return_value=True)
                mock_client.close = AsyncMock()
                mock_client_class.return_value = mock_client

                # Mock save config
                with patch.object(login_screen, "_save_config", AsyncMock()):
                    # Click login button
                    await pilot.click("#login_button")
                    await pilot.pause()

                    # Verify client was created with correct params
                    mock_client_class.assert_called_once_with(
                        api_url="https://test.openproject.org/api/v3",
                        api_key="test_api_key",
                    )

                    # Verify connection was tested
                    mock_client.test_connection.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_authentication_failure(self):
        """Test login with authentication failure."""
        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app
            login_screen = LoginScreen()
            await app.push_screen(login_screen)
            await pilot.pause()

            # Fill in the form
            api_url_input = login_screen.query_one("#api_url")
            api_key_input = login_screen.query_one("#api_key")

            api_url_input.value = "https://test.openproject.org"
            api_key_input.value = "invalid_key"

            # Mock failed connection test
            with patch("src.screens.login.OpenProjectClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client.test_connection = AsyncMock(
                    side_effect=AuthenticationError("Invalid API key")
                )
                mock_client_class.return_value = mock_client

                # Click login button
                await pilot.click("#login_button")
                await pilot.pause()

                # Check for error message
                error_label = login_screen.query_one("#error_message")
                assert error_label is not None
                assert "Invalid API key" in str(error_label.renderable)

    @pytest.mark.asyncio
    async def test_login_empty_fields_validation(self):
        """Test login with empty fields shows validation error."""
        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app
            login_screen = LoginScreen()
            await app.push_screen(login_screen)
            await pilot.pause()

            # Clear any existing values
            api_url_input = login_screen.query_one("#api_url")
            api_key_input = login_screen.query_one("#api_key")
            api_url_input.value = ""
            api_key_input.value = ""

            # Try to login without filling fields
            await pilot.click("#login_button")
            await pilot.pause()

            # Check for error message
            error_label = login_screen.query_one("#error_message")
            assert error_label is not None
            assert "Please fill in all fields" in str(error_label.renderable)

    @pytest.mark.asyncio
    async def test_login_saves_config(self):
        """Test successful login saves configuration."""
        async with OpenProjectApp().run_test() as pilot:
            app = pilot.app
            login_screen = LoginScreen()
            await app.push_screen(login_screen)
            await pilot.pause()

            # Fill in the form
            api_url_input = login_screen.query_one("#api_url")
            api_key_input = login_screen.query_one("#api_key")

            api_url_input.value = "https://test.openproject.org"
            api_key_input.value = "test_api_key"

            # Mock successful connection and config
            with patch("src.screens.login.OpenProjectClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client.test_connection = AsyncMock(return_value=True)
                mock_client.close = AsyncMock()
                mock_client_class.return_value = mock_client

                with patch("src.screens.login.config"):
                    with patch.object(
                        login_screen, "_save_config", AsyncMock()
                    ) as mock_save:
                        # Click login button
                        await pilot.click("#login_button")
                        await pilot.pause()

                        # Verify save_config was called
                        mock_save.assert_called_once_with(
                            "https://test.openproject.org/api/v3", "test_api_key"
                        )
