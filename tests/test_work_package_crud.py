"""Tests for work package CRUD operations."""

import pytest

from src.client import OpenProjectClient
from src.models import WorkPackage, Project, Type, Status, Priority, User


class TestWorkPackageCRUD:
    """Test cases for work package create, read, update, delete operations."""

    @pytest.fixture
    def mock_project(self):
        """Create a mock project."""
        return Project(
            id=1,
            identifier="test-project",
            name="Test Project",
            active=True,
            public=False,
        )

    @pytest.fixture
    def mock_work_package(self):
        """Create a mock work package."""
        return WorkPackage(
            id=1,
            subject="Test Work Package",
            description="Test description",
            lock_version=1,
            type=Type(id=1, name="Task", color="#0066CC"),
            status=Status(id=1, name="New", color="#0066CC"),
            priority=Priority(id=8, name="Normal"),
            assignee=User(id=1, name="John Doe"),
            project=Project(id=1, identifier="test-project", name="Test Project"),
        )

    @pytest.mark.asyncio
    async def test_create_work_package(self, httpx_mock):
        """Test creating a new work package."""
        create_response = {
            "id": 123,
            "subject": "New Task",
            "description": {"raw": "Task description"},
            "lockVersion": 1,
            "_embedded": {
                "type": {"id": 1, "name": "Task", "color": "#0066CC"},
                "status": {"id": 1, "name": "New", "color": "#0066CC"},
                "priority": {"id": 8, "name": "Normal"},
                "project": {
                    "id": 1,
                    "identifier": "test-project",
                    "name": "Test Project",
                },
            },
        }

        httpx_mock.add_response(
            method="POST",
            url="https://test.openproject.com/api/v3/work_packages",
            json=create_response,
        )

        client = OpenProjectClient(
            api_url="https://test.openproject.com/api/v3", api_key="test-key"
        )

        result = await client.create_work_package(
            project_id=1,
            subject="New Task",
            type_id=1,
            description="Task description",
            priority_id=8,
        )

        assert result.id == 123
        assert result.subject == "New Task"
        assert result.description == "Task description"
        assert result.type.name == "Task"
        assert result.status.name == "New"
        assert result.priority.name == "Normal"

    @pytest.mark.asyncio
    async def test_update_work_package(self, httpx_mock):
        """Test updating an existing work package."""
        update_response = {
            "id": 123,
            "subject": "Updated Task",
            "description": {"raw": "Updated description"},
            "lockVersion": 2,
            "_embedded": {
                "type": {"id": 1, "name": "Task", "color": "#0066CC"},
                "status": {"id": 2, "name": "In Progress", "color": "#00CC00"},
                "priority": {"id": 9, "name": "High"},
                "assignee": {"id": 2, "name": "Jane Smith"},
                "project": {
                    "id": 1,
                    "identifier": "test-project",
                    "name": "Test Project",
                },
            },
        }

        httpx_mock.add_response(
            method="PATCH",
            url="https://test.openproject.com/api/v3/work_packages/123",
            json=update_response,
        )

        client = OpenProjectClient(
            api_url="https://test.openproject.com/api/v3", api_key="test-key"
        )

        result = await client.update_work_package(
            work_package_id=123,
            subject="Updated Task",
            description="Updated description",
            status_id=2,
            priority_id=9,
            assignee_id=2,
            lock_version=1,
        )

        assert result.id == 123
        assert result.subject == "Updated Task"
        assert result.description == "Updated description"
        assert result.status.name == "In Progress"
        assert result.priority.name == "High"
        assert result.assignee.name == "Jane Smith"
        assert result.lock_version == 2

    @pytest.mark.asyncio
    async def test_get_types(self, httpx_mock):
        """Test getting available types."""
        types_response = {
            "_embedded": {
                "elements": [
                    {"id": 1, "name": "Task", "color": "#0066CC"},
                    {"id": 2, "name": "Bug", "color": "#CC0000"},
                    {"id": 3, "name": "Feature", "color": "#00CC00"},
                ]
            }
        }

        httpx_mock.add_response(
            method="GET",
            url="https://test.openproject.com/api/v3/projects/1/types",
            json=types_response,
        )

        client = OpenProjectClient(
            api_url="https://test.openproject.com/api/v3", api_key="test-key"
        )

        types = await client.get_types(project_id=1)

        assert len(types) == 3
        assert types[0].name == "Task"
        assert types[1].name == "Bug"
        assert types[2].name == "Feature"

    @pytest.mark.asyncio
    async def test_get_statuses(self, httpx_mock):
        """Test getting available statuses."""
        statuses_response = {
            "_embedded": {
                "elements": [
                    {"id": 1, "name": "New", "color": "#0066CC"},
                    {"id": 2, "name": "In Progress", "color": "#00CC00"},
                    {"id": 3, "name": "Done", "color": "#999999"},
                ]
            }
        }

        httpx_mock.add_response(
            method="GET",
            url="https://test.openproject.com/api/v3/statuses",
            json=statuses_response,
        )

        client = OpenProjectClient(
            api_url="https://test.openproject.com/api/v3", api_key="test-key"
        )

        statuses = await client.get_statuses()

        assert len(statuses) == 3
        assert statuses[0].name == "New"
        assert statuses[1].name == "In Progress"
        assert statuses[2].name == "Done"

    @pytest.mark.asyncio
    async def test_get_priorities(self, httpx_mock):
        """Test getting available priorities."""
        priorities_response = {
            "_embedded": {
                "elements": [
                    {"id": 7, "name": "Low"},
                    {"id": 8, "name": "Normal"},
                    {"id": 9, "name": "High"},
                    {"id": 10, "name": "Immediate"},
                ]
            }
        }

        httpx_mock.add_response(
            method="GET",
            url="https://test.openproject.com/api/v3/priorities",
            json=priorities_response,
        )

        client = OpenProjectClient(
            api_url="https://test.openproject.com/api/v3", api_key="test-key"
        )

        priorities = await client.get_priorities()

        assert len(priorities) == 4
        assert priorities[0].name == "Low"
        assert priorities[1].name == "Normal"
        assert priorities[2].name == "High"
        assert priorities[3].name == "Immediate"

    @pytest.mark.asyncio
    async def test_get_project_members(self, httpx_mock):
        """Test getting project members."""
        members_response = {
            "_embedded": {
                "elements": [
                    {"id": 1, "name": "John Doe"},
                    {"id": 2, "name": "Jane Smith"},
                    {"id": 3, "name": "Bob Johnson"},
                ]
            }
        }

        httpx_mock.add_response(
            method="GET",
            url="https://test.openproject.com/api/v3/projects/1/available_assignees",
            json=members_response,
        )

        client = OpenProjectClient(
            api_url="https://test.openproject.com/api/v3", api_key="test-key"
        )

        members = await client.get_project_members(project_id=1)

        assert len(members) == 3
        assert members[0].name == "John Doe"
        assert members[1].name == "Jane Smith"
        assert members[2].name == "Bob Johnson"

    @pytest.mark.asyncio
    async def test_get_available_statuses_for_new(self, httpx_mock):
        """Test getting available statuses for a new work package."""
        form_response = {
            "_type": "Form",
            "_embedded": {
                "schema": {
                    "status": {
                        "_embedded": {
                            "allowedValues": [
                                {
                                    "id": 1,
                                    "name": "New",
                                    "color": "#0066CC",
                                    "_type": "Status",
                                },
                                {
                                    "id": 2,
                                    "name": "In Progress",
                                    "color": "#00CC00",
                                    "_type": "Status",
                                },
                            ]
                        }
                    }
                }
            },
        }

        httpx_mock.add_response(
            method="POST",
            url="https://test.openproject.com/api/v3/projects/1/work_packages/form",
            json=form_response,
        )

        client = OpenProjectClient(
            api_url="https://test.openproject.com/api/v3", api_key="test-key"
        )

        statuses = await client.get_available_statuses_for_new(project_id=1, type_id=2)

        assert len(statuses) == 2
        assert statuses[0].name == "New"
        assert statuses[1].name == "In Progress"

    @pytest.mark.asyncio
    async def test_get_available_status_transitions(self, httpx_mock):
        """Test getting available status transitions for existing work package."""
        form_response = {
            "_type": "Form",
            "_embedded": {
                "schema": {
                    "status": {
                        "_embedded": {
                            "allowedValues": [
                                {
                                    "id": 2,
                                    "name": "In Progress",
                                    "color": "#00CC00",
                                    "_type": "Status",
                                },
                                {
                                    "id": 3,
                                    "name": "Done",
                                    "color": "#999999",
                                    "_type": "Status",
                                },
                                {
                                    "id": 4,
                                    "name": "On Hold",
                                    "color": "#FFCC00",
                                    "_type": "Status",
                                },
                            ]
                        }
                    }
                }
            },
        }

        httpx_mock.add_response(
            method="POST",
            url="https://test.openproject.com/api/v3/work_packages/123/form",
            json=form_response,
        )

        client = OpenProjectClient(
            api_url="https://test.openproject.com/api/v3", api_key="test-key"
        )

        statuses = await client.get_available_status_transitions(work_package_id=123)

        assert len(statuses) == 3
        assert statuses[0].name == "In Progress"
        assert statuses[1].name == "Done"
        assert statuses[2].name == "On Hold"
