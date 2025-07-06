"""OpenProject API client."""

import base64
import json
from typing import Any, Dict, Optional, List
import httpx

from .models import Project, WorkPackage


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

    async def get_projects(
        self, active: Optional[bool] = None, page: int = 1, page_size: int = 25
    ) -> List[Project]:
        """Fetch projects from the API.

        Args:
            active: Filter by active status
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            List of Project objects
        """
        params = {"offset": (page - 1) * page_size + 1, "pageSize": page_size}

        # Add filters if specified
        filters = []
        if active is not None:
            filters.append(
                {"active": {"operator": "=", "values": ["t" if active else "f"]}}
            )

        if filters:
            params["filters"] = json.dumps(filters)

        response = await self._get("/projects", params=params)
        elements = response.get("_embedded", {}).get("elements", [])
        return [Project.from_hal_json(elem) for elem in elements]

    async def get_work_packages(
        self, project_id: Optional[int] = None, page: int = 1, page_size: int = 25
    ) -> List[WorkPackage]:
        """Fetch work packages from the API.

        Args:
            project_id: Filter by project ID
            page: Page number (1-based)
            page_size: Number of items per page

        Returns:
            List of WorkPackage objects
        """
        params = {"offset": (page - 1) * page_size + 1, "pageSize": page_size}

        # Use project-specific endpoint if project_id is provided
        if project_id:
            endpoint = f"/projects/{project_id}/work_packages"
        else:
            endpoint = "/work_packages"

        response = await self._get(endpoint, params=params)
        elements = response.get("_embedded", {}).get("elements", [])
        return [WorkPackage.from_hal_json(elem) for elem in elements]
