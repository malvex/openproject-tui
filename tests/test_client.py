"""Tests for the OpenProject API client."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from src.client import OpenProjectClient, AuthenticationError, APIError


class TestOpenProjectClient:
    """Test cases for OpenProjectClient."""

    @pytest.fixture
    def client(self):
        """Create a test client instance."""
        return OpenProjectClient(
            api_url="https://openproject.example.com/api/v3", api_key="test_key"
        )

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initializes with proper configuration."""
        client = OpenProjectClient(
            api_url="https://openproject.example.com/api/v3", api_key="test_key"
        )
        assert client.api_url == "https://openproject.example.com/api/v3"
        assert client.api_key == "test_key"
        assert (
            client.headers["Authorization"] == "Basic YXBpa2V5OnRlc3Rfa2V5"
        )  # base64 of apikey:test_key

    @pytest.mark.asyncio
    async def test_client_without_api_key_raises_error(self):
        """Test client raises error when API key is missing."""
        with pytest.raises(ValueError, match="API key is required"):
            OpenProjectClient(
                api_url="https://openproject.example.com/api/v3", api_key=""
            )

    @pytest.mark.asyncio
    async def test_test_connection_success(self, client):
        """Test successful connection test."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "_type": "Root",
            "_links": {
                "self": {"href": "/api/v3"},
                "projects": {"href": "/api/v3/projects"},
            },
        }

        with patch.object(
            client._client, "get", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await client.test_connection()
            assert result is True

    @pytest.mark.asyncio
    async def test_test_connection_authentication_failure(self, client):
        """Test connection test with authentication failure."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "401 Unauthorized", request=MagicMock(), response=mock_response
        )

        with patch.object(
            client._client, "get", new_callable=AsyncMock, return_value=mock_response
        ):
            with pytest.raises(AuthenticationError, match="Authentication failed"):
                await client.test_connection()

    @pytest.mark.asyncio
    async def test_get_request_success(self, client):
        """Test successful GET request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}

        with patch.object(
            client._client, "get", new_callable=AsyncMock, return_value=mock_response
        ):
            result = await client._get("/test")
            assert result == {"data": "test"}

    @pytest.mark.asyncio
    async def test_get_request_with_params(self, client):
        """Test GET request with query parameters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}

        with patch.object(
            client._client, "get", new_callable=AsyncMock, return_value=mock_response
        ) as mock_get:
            await client._get("/test", params={"filter": "active"})
            mock_get.assert_called_once_with("/test", params={"filter": "active"})

    @pytest.mark.asyncio
    async def test_get_request_api_error(self, client):
        """Test GET request with API error."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500 Internal Server Error", request=MagicMock(), response=mock_response
        )

        with patch.object(
            client._client, "get", new_callable=AsyncMock, return_value=mock_response
        ):
            with pytest.raises(APIError, match="API request failed"):
                await client._get("/test")

    @pytest.mark.asyncio
    async def test_close_client(self, client):
        """Test client cleanup."""
        with patch.object(
            client._client, "aclose", new_callable=AsyncMock
        ) as mock_close:
            await client.close()
            mock_close.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test client as async context manager."""
        client = OpenProjectClient(
            api_url="https://openproject.example.com/api/v3", api_key="test_key"
        )

        with patch.object(
            client._client, "aclose", new_callable=AsyncMock
        ) as mock_close:
            async with client:
                pass
            mock_close.assert_called_once()
