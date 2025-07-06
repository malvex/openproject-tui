"""Tests for data models."""

from datetime import datetime

from src.models import Project, WorkPackage, User


class TestUserModel:
    """Test cases for User model."""

    def test_user_from_hal_json(self):
        """Test creating User from HAL+JSON response."""
        hal_data = {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "avatar": "https://example.com/avatar.jpg",
            "_type": "User",
            "_links": {
                "self": {"href": "/api/v3/users/1"},
                "showUser": {"href": "/users/1"},
            },
        }

        user = User.from_hal_json(hal_data)

        assert user.id == 1
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.avatar_url == "https://example.com/avatar.jpg"

    def test_user_display_name(self):
        """Test user display name formatting."""
        user = User(id=1, name="John Doe", email="john@example.com")
        assert str(user) == "John Doe"

        user_no_name = User(id=2, name="", email="jane@example.com")
        assert str(user_no_name) == "jane@example.com"


class TestProjectModel:
    """Test cases for Project model."""

    def test_project_from_hal_json(self):
        """Test creating Project from HAL+JSON response."""
        hal_data = {
            "id": 1,
            "identifier": "demo-project",
            "name": "Demo Project",
            "active": True,
            "public": False,
            "description": {
                "format": "markdown",
                "raw": "A demo project",
                "html": "<p>A demo project</p>",
            },
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-02T00:00:00Z",
            "_type": "Project",
            "_links": {
                "self": {"href": "/api/v3/projects/1"},
                "workPackages": {"href": "/api/v3/projects/1/work_packages"},
            },
        }

        project = Project.from_hal_json(hal_data)

        assert project.id == 1
        assert project.identifier == "demo-project"
        assert project.name == "Demo Project"
        assert project.active is True
        assert project.public is False
        assert project.description == "A demo project"
        assert project.created_at == datetime.fromisoformat(
            "2024-01-01T00:00:00Z".replace("Z", "+00:00")
        )
        assert project.updated_at == datetime.fromisoformat(
            "2024-01-02T00:00:00Z".replace("Z", "+00:00")
        )

    def test_project_from_hal_json_minimal(self):
        """Test creating Project from minimal HAL+JSON response."""
        hal_data = {
            "id": 2,
            "identifier": "minimal",
            "name": "Minimal Project",
            "_type": "Project",
            "_links": {"self": {"href": "/api/v3/projects/2"}},
        }

        project = Project.from_hal_json(hal_data)

        assert project.id == 2
        assert project.identifier == "minimal"
        assert project.name == "Minimal Project"
        assert project.active is True  # default
        assert project.public is False  # default
        assert project.description == ""
        assert project.created_at is None
        assert project.updated_at is None


class TestWorkPackageModel:
    """Test cases for WorkPackage model."""

    def test_work_package_from_hal_json(self):
        """Test creating WorkPackage from HAL+JSON response."""
        hal_data = {
            "id": 1,
            "subject": "Fix login bug",
            "description": {
                "format": "markdown",
                "raw": "Login fails with special characters",
                "html": "<p>Login fails with special characters</p>",
            },
            "startDate": "2024-01-01",
            "dueDate": "2024-01-15",
            "estimatedTime": "PT8H",
            "percentageDone": 50,
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-02T00:00:00Z",
            "_type": "WorkPackage",
            "_embedded": {
                "status": {
                    "id": 1,
                    "name": "In Progress",
                    "color": "#0066CC",
                    "_type": "Status",
                },
                "type": {"id": 2, "name": "Bug", "color": "#CC0000", "_type": "Type"},
                "priority": {"id": 8, "name": "High", "_type": "Priority"},
                "project": {
                    "id": 1,
                    "identifier": "demo-project",
                    "name": "Demo Project",
                    "_type": "Project",
                },
                "author": {"id": 1, "name": "John Doe", "_type": "User"},
                "assignee": {"id": 2, "name": "Jane Smith", "_type": "User"},
            },
            "_links": {"self": {"href": "/api/v3/work_packages/1"}},
        }

        work_package = WorkPackage.from_hal_json(hal_data)

        assert work_package.id == 1
        assert work_package.subject == "Fix login bug"
        assert work_package.description == "Login fails with special characters"
        assert work_package.start_date == "2024-01-01"
        assert work_package.due_date == "2024-01-15"
        assert work_package.estimated_hours == 8.0
        assert work_package.percentage_done == 50

        assert work_package.status.name == "In Progress"
        assert work_package.status.color == "#0066CC"
        assert work_package.type.name == "Bug"
        assert work_package.priority.name == "High"
        assert work_package.project.name == "Demo Project"
        assert work_package.author.name == "John Doe"
        assert work_package.assignee.name == "Jane Smith"

    def test_work_package_from_hal_json_minimal(self):
        """Test creating WorkPackage from minimal HAL+JSON response."""
        hal_data = {
            "id": 2,
            "subject": "Minimal work package",
            "_type": "WorkPackage",
            "_embedded": {
                "status": {"id": 1, "name": "New", "_type": "Status"},
                "project": {"id": 1, "name": "Project", "_type": "Project"},
            },
            "_links": {"self": {"href": "/api/v3/work_packages/2"}},
        }

        work_package = WorkPackage.from_hal_json(hal_data)

        assert work_package.id == 2
        assert work_package.subject == "Minimal work package"
        assert work_package.description == ""
        assert work_package.percentage_done == 0
        assert work_package.status.name == "New"
        assert work_package.project.name == "Project"
        assert work_package.author is None
        assert work_package.assignee is None

    def test_work_package_estimated_time_parsing(self):
        """Test parsing of ISO 8601 duration for estimated time."""
        test_cases = [
            ("PT8H", 8.0),  # 8 hours
            ("PT4H30M", 4.5),  # 4.5 hours
            ("PT30M", 0.5),  # 30 minutes
            ("PT1H45M", 1.75),  # 1 hour 45 minutes
            ("PT2H15M", 2.25),  # 2 hours 15 minutes
            (None, None),  # No estimate
        ]

        for iso_duration, expected_hours in test_cases:
            hal_data = {
                "id": 1,
                "subject": "Test",
                "estimatedTime": iso_duration,
                "_type": "WorkPackage",
                "_embedded": {
                    "status": {"id": 1, "name": "New", "_type": "Status"},
                    "project": {"id": 1, "name": "Project", "_type": "Project"},
                },
            }
            work_package = WorkPackage.from_hal_json(hal_data)
            assert work_package.estimated_hours == expected_hours
