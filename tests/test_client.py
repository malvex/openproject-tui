"""Tests for the OpenProject API client using pytest-httpx."""

import json
import pytest
from pytest_httpx import HTTPXMock

from src.client import OpenProjectClient, AuthenticationError, APIError
from src.models import Project, WorkPackage
from .test_fixtures import (
    ROOT_RESPONSE,
    PROJECTS_LIST_RESPONSE,
    PROJECTS_EMPTY_RESPONSE,
    WORK_PACKAGES_LIST_RESPONSE,
    WORK_PACKAGES_EMPTY_RESPONSE,
    ERROR_UNAUTHORIZED,
    ERROR_INTERNAL_SERVER,
)


class TestOpenProjectClient:
    """Test cases for OpenProject API client using pytest-httpx."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return OpenProjectClient(
            api_url="https://openproject.example.com/api/v3", api_key="test_key"
        )

    @pytest.fixture
    def base_url(self):
        """Base URL for the API."""
        return "https://openproject.example.com/api/v3"

    def test_client_initialization(self):
        """Test client initializes with proper configuration."""
        client = OpenProjectClient(
            api_url="https://openproject.example.com/api/v3", api_key="test_key"
        )
        assert client.api_url == "https://openproject.example.com/api/v3"
        assert client.api_key == "test_key"
        # Verify Basic auth header is properly encoded
        assert client.headers["Authorization"] == "Basic YXBpa2V5OnRlc3Rfa2V5"

    def test_client_without_api_key_raises_error(self):
        """Test client raises error when API key is missing."""
        with pytest.raises(ValueError, match="API key is required"):
            OpenProjectClient(
                api_url="https://openproject.example.com/api/v3", api_key=""
            )

    @pytest.mark.asyncio
    async def test_test_connection_success(
        self, client, httpx_mock: HTTPXMock, base_url
    ):
        """Test successful connection test."""
        httpx_mock.add_response(url=f"{base_url}/", json=ROOT_RESPONSE)

        result = await client.test_connection()
        assert result is True

    @pytest.mark.asyncio
    async def test_test_connection_authentication_failure(
        self, client, httpx_mock: HTTPXMock, base_url
    ):
        """Test connection with authentication failure."""
        httpx_mock.add_response(
            url=f"{base_url}/", status_code=401, json=ERROR_UNAUTHORIZED
        )

        with pytest.raises(AuthenticationError):
            await client.test_connection()

    @pytest.mark.asyncio
    async def test_get_projects(self, client, httpx_mock: HTTPXMock, base_url):
        """Test fetching projects list."""
        httpx_mock.add_response(
            url=f"{base_url}/projects?offset=1&pageSize=25", json=PROJECTS_LIST_RESPONSE
        )

        projects = await client.get_projects()

        assert len(projects) == 2
        assert all(isinstance(p, Project) for p in projects)
        assert projects[0].identifier == "demo-project"
        assert projects[0].name == "Demo Project"
        assert projects[1].identifier == "test-project"
        assert projects[1].name == "Test Project"

    @pytest.mark.asyncio
    async def test_get_projects_with_filters(
        self, client, httpx_mock: HTTPXMock, base_url
    ):
        """Test fetching projects with filters."""
        filters = json.dumps([{"active": {"operator": "=", "values": ["t"]}}])
        httpx_mock.add_response(
            url=f"{base_url}/projects?offset=11&pageSize=10&filters={filters}",
            json=PROJECTS_EMPTY_RESPONSE,
        )

        projects = await client.get_projects(active=True, page=2, page_size=10)
        assert len(projects) == 0

    @pytest.mark.asyncio
    async def test_get_work_packages(self, client, httpx_mock: HTTPXMock, base_url):
        """Test fetching work packages."""
        httpx_mock.add_response(
            url=f"{base_url}/work_packages?offset=1&pageSize=25",
            json=WORK_PACKAGES_LIST_RESPONSE,
        )

        work_packages = await client.get_work_packages()

        assert len(work_packages) == 1
        assert isinstance(work_packages[0], WorkPackage)
        assert work_packages[0].subject == "Fix login bug"
        assert work_packages[0].status.name == "New"
        assert work_packages[0].type.name == "Bug"
        assert work_packages[0].priority.name == "High"

    @pytest.mark.asyncio
    async def test_get_project_work_packages(
        self, client, httpx_mock: HTTPXMock, base_url
    ):
        """Test fetching work packages for a specific project."""
        httpx_mock.add_response(
            url=f"{base_url}/projects/1/work_packages?offset=1&pageSize=25",
            json=WORK_PACKAGES_EMPTY_RESPONSE,
        )

        work_packages = await client.get_work_packages(project_id=1)
        assert len(work_packages) == 0

    @pytest.mark.asyncio
    async def test_api_error(self, client, httpx_mock: HTTPXMock, base_url):
        """Test API error handling."""
        httpx_mock.add_response(
            url=f"{base_url}/test", status_code=500, json=ERROR_INTERNAL_SERVER
        )

        with pytest.raises(APIError):
            await client._get("/test")

    @pytest.mark.asyncio
    async def test_multiple_requests(self, client, httpx_mock: HTTPXMock, base_url):
        """Test multiple API calls in sequence."""
        # Add multiple responses with exact URLs
        httpx_mock.add_response(
            url=f"{base_url}/projects?offset=1&pageSize=25", json=PROJECTS_LIST_RESPONSE
        )
        httpx_mock.add_response(
            url=f"{base_url}/work_packages?offset=1&pageSize=25",
            json=WORK_PACKAGES_LIST_RESPONSE,
        )

        # Make multiple calls
        projects = await client.get_projects()
        work_packages = await client.get_work_packages()

        assert len(projects) == 2
        assert len(work_packages) == 1

        # httpx_mock automatically verifies all mocked calls were made
