"""Data models for OpenProject entities."""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class Status:
    """Work package status."""

    id: int
    name: str
    color: Optional[str] = None


@dataclass
class Type:
    """Work package type."""

    id: int
    name: str
    color: Optional[str] = None


@dataclass
class Priority:
    """Work package priority."""

    id: int
    name: str


@dataclass
class User:
    """User model."""

    id: int
    name: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None

    @classmethod
    def from_hal_json(cls, data: Dict[str, Any]) -> "User":
        """Create User from HAL+JSON response."""
        return cls(
            id=data["id"],
            name=data.get("name", ""),
            email=data.get("email"),
            avatar_url=data.get("avatar"),
        )

    def __str__(self) -> str:
        """Return display name."""
        return self.name or self.email or f"User {self.id}"


@dataclass
class Project:
    """Project model."""

    id: int
    identifier: str
    name: str
    active: bool = True
    public: bool = False
    description: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_hal_json(cls, data: Dict[str, Any]) -> "Project":
        """Create Project from HAL+JSON response."""
        description = ""
        if desc_data := data.get("description"):
            description = desc_data.get("raw", "")

        created_at = None
        if created_str := data.get("createdAt"):
            created_at = datetime.fromisoformat(created_str.replace("Z", "+00:00"))

        updated_at = None
        if updated_str := data.get("updatedAt"):
            updated_at = datetime.fromisoformat(updated_str.replace("Z", "+00:00"))

        return cls(
            id=data["id"],
            identifier=data["identifier"],
            name=data["name"],
            active=data.get("active", True),
            public=data.get("public", False),
            description=description,
            created_at=created_at,
            updated_at=updated_at,
        )


@dataclass
class WorkPackage:
    """Work package model."""

    id: int
    subject: str
    description: str = ""
    start_date: Optional[str] = None
    due_date: Optional[str] = None
    estimated_hours: Optional[float] = None
    percentage_done: int = 0
    status: Optional[Status] = None
    type: Optional[Type] = None
    priority: Optional[Priority] = None
    project: Optional[Project] = None
    author: Optional[User] = None
    assignee: Optional[User] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_hal_json(cls, data: Dict[str, Any]) -> "WorkPackage":
        """Create WorkPackage from HAL+JSON response."""
        description = ""
        if desc_data := data.get("description"):
            description = desc_data.get("raw", "")

        # Parse estimated time from ISO 8601 duration
        estimated_hours = None
        if estimated_time := data.get("estimatedTime"):
            estimated_hours = cls._parse_iso_duration(estimated_time)

        created_at = None
        if created_str := data.get("createdAt"):
            created_at = datetime.fromisoformat(created_str.replace("Z", "+00:00"))

        updated_at = None
        if updated_str := data.get("updatedAt"):
            updated_at = datetime.fromisoformat(updated_str.replace("Z", "+00:00"))

        # Parse embedded resources
        embedded = data.get("_embedded", {})

        status = None
        if status_data := embedded.get("status"):
            status = Status(
                id=status_data["id"],
                name=status_data["name"],
                color=status_data.get("color"),
            )

        type_obj = None
        if type_data := embedded.get("type"):
            type_obj = Type(
                id=type_data["id"], name=type_data["name"], color=type_data.get("color")
            )

        priority = None
        if priority_data := embedded.get("priority"):
            priority = Priority(id=priority_data["id"], name=priority_data["name"])

        project = None
        if project_data := embedded.get("project"):
            project = Project(
                id=project_data["id"],
                identifier=project_data.get("identifier", ""),
                name=project_data["name"],
            )

        author = None
        if author_data := embedded.get("author"):
            author = User(id=author_data["id"], name=author_data.get("name", ""))

        assignee = None
        if assignee_data := embedded.get("assignee"):
            assignee = User(id=assignee_data["id"], name=assignee_data.get("name", ""))

        return cls(
            id=data["id"],
            subject=data["subject"],
            description=description,
            start_date=data.get("startDate"),
            due_date=data.get("dueDate"),
            estimated_hours=estimated_hours,
            percentage_done=data.get("percentageDone", 0),
            status=status,
            type=type_obj,
            priority=priority,
            project=project,
            author=author,
            assignee=assignee,
            created_at=created_at,
            updated_at=updated_at,
        )

    @staticmethod
    def _parse_iso_duration(duration: str) -> float:
        """Parse ISO 8601 duration to hours.

        Examples:
            PT8H -> 8.0
            PT4H30M -> 4.5
            PT30M -> 0.5
        """
        if not duration or not duration.startswith("PT"):
            return 0.0

        # Remove PT prefix
        duration = duration[2:]

        hours = 0.0
        minutes = 0.0

        # Parse hours
        if "H" in duration:
            hours_part = duration.split("H")[0]
            hours = float(hours_part)
            duration = duration.split("H")[1]

        # Parse minutes
        if "M" in duration:
            minutes_part = duration.split("M")[0]
            minutes = float(minutes_part)

        return hours + (minutes / 60.0)
