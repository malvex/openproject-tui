"""OpenProject API client."""

import base64
import json
from typing import Any, Dict, Optional, List
import httpx

from .models import Priority, Project, Status, Type, User, WorkPackage


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

        # Use the API URL as-is since it should already include /api/v3
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
            # Try to get error details from response
            error_detail = ""
            try:
                error_data = e.response.json()
                if "message" in error_data:
                    error_detail = f": {error_data['message']}"
                elif "_embedded" in error_data and "errors" in error_data["_embedded"]:
                    errors = error_data["_embedded"]["errors"]
                    error_messages = [err.get("message", "") for err in errors.values()]
                    error_detail = f": {', '.join(error_messages)}"
            except Exception:
                pass
            raise APIError(
                f"API request failed (HTTP {e.response.status_code}){error_detail}"
            )
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
            # Try to get error details from response
            error_detail = ""
            try:
                error_data = e.response.json()
                if "message" in error_data:
                    error_detail = f": {error_data['message']}"
                elif "_embedded" in error_data and "errors" in error_data["_embedded"]:
                    errors = error_data["_embedded"]["errors"]
                    error_messages = [err.get("message", "") for err in errors.values()]
                    error_detail = f": {', '.join(error_messages)}"
            except Exception:
                pass
            raise APIError(
                f"API request failed (HTTP {e.response.status_code}){error_detail}"
            )
        except AuthenticationError:
            raise  # Re-raise authentication errors as-is
        except Exception as e:
            raise APIError(f"Request failed: {e}")

    async def _post(
        self, endpoint: str, json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a POST request to the API.

        Args:
            endpoint: API endpoint to call
            json: JSON data to send

        Returns:
            JSON response data

        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API request fails
        """
        try:
            response = await self._client.post(endpoint, json=json)
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
            # Try to get error details from response
            error_detail = ""
            try:
                error_data = e.response.json()
                if "message" in error_data:
                    error_detail = f": {error_data['message']}"
                elif "_embedded" in error_data and "errors" in error_data["_embedded"]:
                    errors = error_data["_embedded"]["errors"]
                    error_messages = [err.get("message", "") for err in errors.values()]
                    error_detail = f": {', '.join(error_messages)}"
            except Exception:
                pass
            raise APIError(
                f"API request failed (HTTP {e.response.status_code}){error_detail}"
            )
        except AuthenticationError:
            raise  # Re-raise authentication errors as-is
        except Exception as e:
            raise APIError(f"Request failed: {e}")

    async def _patch(
        self, endpoint: str, json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a PATCH request to the API.

        Args:
            endpoint: API endpoint to call
            json: JSON data to send

        Returns:
            JSON response data

        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API request fails
        """
        try:
            response = await self._client.patch(endpoint, json=json)
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
            # Try to get error details from response
            error_detail = ""
            try:
                error_data = e.response.json()
                if "message" in error_data:
                    error_detail = f": {error_data['message']}"
                elif "_embedded" in error_data and "errors" in error_data["_embedded"]:
                    errors = error_data["_embedded"]["errors"]
                    error_messages = [err.get("message", "") for err in errors.values()]
                    error_detail = f": {', '.join(error_messages)}"
            except Exception:
                pass
            raise APIError(
                f"API request failed (HTTP {e.response.status_code}){error_detail}"
            )
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
        params = {
            "offset": (page - 1) * page_size + 1,
            "pageSize": page_size,
        }

        # Use project-specific endpoint if project_id is provided
        if project_id:
            endpoint = f"/projects/{project_id}/work_packages"
        else:
            endpoint = "/work_packages"

        response = await self._get(endpoint, params=params)
        elements = response.get("_embedded", {}).get("elements", [])
        return [WorkPackage.from_hal_json(elem) for elem in elements]

    async def create_work_package(
        self,
        project_id: int,
        subject: str,
        type_id: int,
        description: Optional[str] = None,
        assignee_id: Optional[int] = None,
        status_id: Optional[int] = None,
        priority_id: Optional[int] = None,
    ) -> WorkPackage:
        """Create a new work package.

        Args:
            project_id: ID of the project
            subject: Subject/title of the work package
            type_id: ID of the work package type
            description: Optional description
            assignee_id: Optional ID of the assignee
            status_id: Optional ID of the status
            priority_id: Optional ID of the priority

        Returns:
            Created WorkPackage object
        """
        data = {
            "subject": subject,
            "_links": {
                "project": {"href": f"/api/v3/projects/{project_id}"},
                "type": {"href": f"/api/v3/types/{type_id}"},
            },
        }

        if description:
            data["description"] = {"raw": description}
        if assignee_id:
            data["_links"]["assignee"] = {"href": f"/api/v3/users/{assignee_id}"}
        if status_id:
            data["_links"]["status"] = {"href": f"/api/v3/statuses/{status_id}"}
        if priority_id:
            data["_links"]["priority"] = {"href": f"/api/v3/priorities/{priority_id}"}

        response = await self._post("/work_packages", json=data)
        return WorkPackage.from_hal_json(response)

    async def update_work_package(
        self,
        work_package_id: int,
        subject: Optional[str] = None,
        description: Optional[str] = None,
        assignee_id: Optional[int] = None,
        status_id: Optional[int] = None,
        priority_id: Optional[int] = None,
        lock_version: Optional[int] = None,
    ) -> WorkPackage:
        """Update an existing work package.

        Args:
            work_package_id: ID of the work package to update
            subject: Optional new subject
            description: Optional new description
            assignee_id: Optional new assignee ID (use 0 to unassign)
            status_id: Optional new status ID
            priority_id: Optional new priority ID
            lock_version: Lock version for optimistic locking

        Returns:
            Updated WorkPackage object
        """
        data = {}
        if lock_version is not None:
            data["lockVersion"] = lock_version

        if subject is not None:
            data["subject"] = subject
        if description is not None:
            data["description"] = {"raw": description}

        # Build _links if needed
        links = {}
        if assignee_id is not None:
            if assignee_id == 0:
                links["assignee"] = {"href": None}  # Unassign
            else:
                links["assignee"] = {"href": f"/api/v3/users/{assignee_id}"}
        if status_id is not None:
            links["status"] = {"href": f"/api/v3/statuses/{status_id}"}
        if priority_id is not None:
            links["priority"] = {"href": f"/api/v3/priorities/{priority_id}"}

        if links:
            data["_links"] = links

        response = await self._patch(f"/work_packages/{work_package_id}", json=data)
        return WorkPackage.from_hal_json(response)

    async def get_types(self, project_id: Optional[int] = None) -> List[Type]:
        """Get available work package types.

        Args:
            project_id: Optional project ID to filter types

        Returns:
            List of Type objects
        """
        endpoint = f"/projects/{project_id}/types" if project_id else "/types"
        response = await self._get(endpoint)
        elements = response.get("_embedded", {}).get("elements", [])
        return [Type.from_hal_json(elem) for elem in elements]

    async def get_statuses(self) -> List[Status]:
        """Get available statuses.

        Returns:
            List of Status objects
        """
        response = await self._get("/statuses")
        elements = response.get("_embedded", {}).get("elements", [])
        return [Status.from_hal_json(elem) for elem in elements]

    async def get_priorities(self) -> List[Priority]:
        """Get available priorities.

        Returns:
            List of Priority objects
        """
        response = await self._get("/priorities")
        elements = response.get("_embedded", {}).get("elements", [])
        return [Priority.from_hal_json(elem) for elem in elements]

    async def get_project_members(self, project_id: int) -> List[User]:
        """Get members of a specific project.

        Args:
            project_id: Project ID

        Returns:
            List of User objects who are members of the project
        """
        response = await self._get(f"/projects/{project_id}/available_assignees")
        elements = response.get("_embedded", {}).get("elements", [])
        return [User.from_hal_json(elem) for elem in elements]

    async def get_work_package_form(
        self,
        project_id: Optional[int] = None,
        type_id: Optional[int] = None,
        work_package_id: Optional[int] = None,
        lock_version: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get the work package form with schema and allowed values.

        Args:
            project_id: Project ID (required for new work packages)
            type_id: Optional work package type ID
            work_package_id: Optional existing work package ID for updates
            lock_version: Lock version for existing work packages

        Returns:
            Form response with schema and allowed values
        """
        if work_package_id:
            # Get form for updating existing work package
            endpoint = f"/work_packages/{work_package_id}/form"
            data = {}
            if lock_version is not None:
                data["lockVersion"] = lock_version
            if type_id:
                # If changing type, include it in the request
                data["_links"] = {"type": {"href": f"/api/v3/types/{type_id}"}}
        else:
            # Get form for creating new work package
            if not project_id:
                raise ValueError("project_id is required for new work packages")
            endpoint = f"/projects/{project_id}/work_packages/form"
            data = {"_links": {}}
            if type_id:
                data["_links"]["type"] = {"href": f"/api/v3/types/{type_id}"}

        return await self._post(endpoint, json=data)

    async def get_available_statuses_for_new(
        self, project_id: int, type_id: int
    ) -> List[Status]:
        """Get available statuses for a new work package of a specific type.

        Args:
            project_id: Project ID
            type_id: Work package type ID

        Returns:
            List of Status objects available for new work packages of this type
        """
        try:
            # Get the form which includes allowed values for status
            form_response = await self.get_work_package_form(project_id, type_id)

            # Extract allowed statuses from the schema
            schema = form_response.get("_embedded", {}).get("schema", {})
            status_schema = schema.get("status", {})
            allowed_values = status_schema.get("_embedded", {}).get("allowedValues", [])

            # Convert to Status objects
            statuses = []
            for status_data in allowed_values:
                if (
                    isinstance(status_data, dict)
                    and status_data.get("_type") == "Status"
                ):
                    statuses.append(Status.from_hal_json(status_data))

            return statuses if statuses else await self.get_statuses()

        except Exception as e:
            print(f"Could not get allowed statuses from form: {e}")
            # Fallback to all statuses
            return await self.get_statuses()

    async def get_available_status_transitions(
        self,
        work_package_id: int,
        type_id: Optional[int] = None,
        lock_version: Optional[int] = None,
    ) -> List[Status]:
        """Get available status transitions for an existing work package.

        Args:
            work_package_id: Work package ID
            type_id: Optional new type ID if type is being changed
            lock_version: Optional lock version

        Returns:
            List of Status objects that the work package can transition to
        """
        try:
            # Get the form for the work package which includes allowed status transitions
            form_response = await self.get_work_package_form(
                work_package_id=work_package_id,
                type_id=type_id,
                lock_version=lock_version,
            )

            # Extract allowed statuses from the schema
            schema = form_response.get("_embedded", {}).get("schema", {})
            status_schema = schema.get("status", {})
            allowed_values = status_schema.get("_embedded", {}).get("allowedValues", [])

            # Convert to Status objects
            statuses = []
            for status_data in allowed_values:
                if (
                    isinstance(status_data, dict)
                    and status_data.get("_type") == "Status"
                ):
                    statuses.append(Status.from_hal_json(status_data))

            # Also get the current status from the payload if available
            payload = form_response.get("_embedded", {}).get("payload", {})
            current_status = payload.get("_embedded", {}).get("status")
            if (
                current_status
                and isinstance(current_status, dict)
                and current_status.get("_type") == "Status"
            ):
                current_status_obj = Status.from_hal_json(current_status)
                # Make sure current status is in the list (it should be, but just in case)
                if not any(s.id == current_status_obj.id for s in statuses):
                    statuses.insert(0, current_status_obj)

            return statuses if statuses else await self.get_statuses()

        except Exception as e:
            print(f"Could not get allowed status transitions from form: {e}")
            # Fallback to all statuses
            return await self.get_statuses()
