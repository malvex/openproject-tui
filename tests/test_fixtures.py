"""Test fixtures and mock data for OpenProject API responses."""

# Root API response
ROOT_RESPONSE = {
    "_type": "Root",
    "_links": {
        "self": {"href": "/api/v3"},
        "projects": {"href": "/api/v3/projects"},
        "workPackages": {"href": "/api/v3/work_packages"},
        "users": {"href": "/api/v3/users"},
        "types": {"href": "/api/v3/types"},
        "statuses": {"href": "/api/v3/statuses"},
        "priorities": {"href": "/api/v3/priorities"},
    },
}

# Projects responses
PROJECTS_LIST_RESPONSE = {
    "_embedded": {
        "elements": [
            {
                "id": 1,
                "identifier": "demo-project",
                "name": "Demo Project",
                "active": True,
                "public": False,
                "description": {
                    "format": "markdown",
                    "raw": "A demo project for testing",
                    "html": "<p>A demo project for testing</p>",
                },
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-02T00:00:00Z",
                "_type": "Project",
                "_links": {
                    "self": {"href": "/api/v3/projects/1"},
                    "workPackages": {"href": "/api/v3/projects/1/work_packages"},
                    "categories": {"href": "/api/v3/projects/1/categories"},
                    "versions": {"href": "/api/v3/projects/1/versions"},
                },
            },
            {
                "id": 2,
                "identifier": "test-project",
                "name": "Test Project",
                "active": True,
                "public": True,
                "description": {
                    "format": "markdown",
                    "raw": "A test project",
                    "html": "<p>A test project</p>",
                },
                "createdAt": "2024-01-01T00:00:00Z",
                "updatedAt": "2024-01-02T00:00:00Z",
                "_type": "Project",
                "_links": {
                    "self": {"href": "/api/v3/projects/2"},
                    "workPackages": {"href": "/api/v3/projects/2/work_packages"},
                },
            },
        ]
    },
    "_type": "Collection",
    "total": 2,
    "count": 2,
    "pageSize": 25,
    "offset": 1,
}

PROJECTS_EMPTY_RESPONSE = {
    "_embedded": {"elements": []},
    "_type": "Collection",
    "total": 0,
    "count": 0,
}

# Work packages responses
WORK_PACKAGES_LIST_RESPONSE = {
    "_embedded": {
        "elements": [
            {
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
                        "name": "New",
                        "color": "#0066CC",
                        "_type": "Status",
                    },
                    "type": {
                        "id": 2,
                        "name": "Bug",
                        "color": "#CC0000",
                        "_type": "Type",
                    },
                    "priority": {"id": 8, "name": "High", "_type": "Priority"},
                    "project": {
                        "id": 1,
                        "identifier": "demo-project",
                        "name": "Demo Project",
                        "_type": "Project",
                    },
                    "author": {
                        "id": 1,
                        "name": "John Doe",
                        "email": "john@example.com",
                        "_type": "User",
                    },
                    "assignee": {
                        "id": 2,
                        "name": "Jane Smith",
                        "email": "jane@example.com",
                        "_type": "User",
                    },
                },
                "_links": {
                    "self": {"href": "/api/v3/work_packages/1"},
                    "project": {"href": "/api/v3/projects/1"},
                    "activities": {"href": "/api/v3/work_packages/1/activities"},
                    "attachments": {"href": "/api/v3/work_packages/1/attachments"},
                },
            }
        ]
    },
    "_type": "Collection",
    "total": 1,
    "count": 1,
    "pageSize": 25,
    "offset": 1,
}

WORK_PACKAGES_EMPTY_RESPONSE = {
    "_embedded": {"elements": []},
    "_type": "Collection",
    "total": 0,
    "count": 0,
}

# Error responses
ERROR_UNAUTHORIZED = {
    "_type": "Error",
    "errorIdentifier": "urn:openproject-org:api:v3:errors:Unauthenticated",
    "message": "You need to be authenticated to access this resource.",
}

ERROR_NOT_FOUND = {
    "_type": "Error",
    "errorIdentifier": "urn:openproject-org:api:v3:errors:NotFound",
    "message": "The requested resource could not be found.",
}

ERROR_INTERNAL_SERVER = {
    "_type": "Error",
    "errorIdentifier": "urn:openproject-org:api:v3:errors:InternalServerError",
    "message": "An internal server error occurred.",
}


# Test data helpers
def get_project_by_id(project_id: int):
    """Get a specific project from the test data."""
    for project in PROJECTS_LIST_RESPONSE["_embedded"]["elements"]:
        if project["id"] == project_id:
            return project
    return None


def get_work_package_by_id(wp_id: int):
    """Get a specific work package from the test data."""
    for wp in WORK_PACKAGES_LIST_RESPONSE["_embedded"]["elements"]:
        if wp["id"] == wp_id:
            return wp
    return None
