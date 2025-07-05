"""OpenProject API client."""

import base64
from typing import Any, Dict, Optional
import httpx


class AuthenticationError(Exception):
    """Raised when authentication fails."""


class APIError(Exception):
    """Raised when an API request fails."""


class OpenProjectClient:
    """Client for interacting with the OpenProject API."""

    def __init__(self, api_url: str, api_key: str, timeout: int = 30):
        """Initialize the client.

        Args:
            api_url: Base URL for the OpenProject API
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        if not api_key:
            raise ValueError("API key is required")

        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

        # Create Basic Auth header
        auth_string = base64.b64encode(f"apikey:{api_key}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {auth_string}",
            "Content-Type": "application/json",
            "Accept": "application/hal+json",
        }

        self._client = httpx.AsyncClient(
            base_url=self.api_url,
            headers=self.headers,
            timeout=self.timeout,
        )

    async def test_connection(self) -> bool:
        """Test the connection to the API.

        Returns:
            True if connection is successful

        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API request fails
        """
        try:
            response = await self._client.get("/")
            if response.status_code == 401:
                raise AuthenticationError(
                    "Authentication failed. Please check your API key."
                )
            response.raise_for_status()
            return True
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError(
                    "Authentication failed. Please check your API key."
                )
            raise APIError(f"API request failed: {e}")
        except AuthenticationError:
            raise  # Re-raise authentication errors as-is
        except Exception as e:
            raise APIError(f"Connection failed: {e}")

    async def _get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a GET request to the API.

        Args:
            endpoint: API endpoint to call
            params: Query parameters

        Returns:
            JSON response data

        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API request fails
        """
        try:
            response = await self._client.get(endpoint, params=params)
            if response.status_code == 401:
                raise AuthenticationError(
                    "Authentication failed. Please check your API key."
                )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise AuthenticationError(
                    "Authentication failed. Please check your API key."
                )
            raise APIError(f"API request failed: {e}")
        except AuthenticationError:
            raise  # Re-raise authentication errors as-is
        except Exception as e:
            raise APIError(f"Request failed: {e}")

    async def close(self):
        """Close the client connection."""
        await self._client.aclose()

    async def __aenter__(self):
        """Enter async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager."""
        await self.close()
