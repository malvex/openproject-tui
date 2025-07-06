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

    @classmethod
    def from_hal_json(cls, data: Dict[str, Any]) -> "Status":
        """Create Status from HAL+JSON response."""
        return cls(
            id=data["id"],
            name=data["name"],
            color=data.get("color"),
        )


@dataclass
class Type:
    """Work package type."""

    id: int
    name: str
    color: Optional[str] = None

    @classmethod
    def from_hal_json(cls, data: Dict[str, Any]) -> "Type":
        """Create Type from HAL+JSON response."""
        return cls(
            id=data["id"],
            name=data["name"],
            color=data.get("color"),
        )


@dataclass
class Priority:
    """Work package priority."""

    id: int
    name: str

    @classmethod
    def from_hal_json(cls, data: Dict[str, Any]) -> "Priority":
        """Create Priority from HAL+JSON response."""
        return cls(
            id=data["id"],
            name=data["name"],
        )


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
            identifier=data.get("identifier", ""),
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
    lock_version: Optional[int] = None

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

        # Parse embedded resources - OpenProject can put these in either _embedded or _links
        embedded = data.get("_embedded", {})
        links = data.get("_links", {})

        # Parse related resources
        status = cls._parse_status(embedded.get("status"), links.get("status"))
        type_obj = cls._parse_type(embedded.get("type"), links.get("type"))
        priority = cls._parse_priority(embedded.get("priority"), links.get("priority"))
        project = cls._parse_project(embedded.get("project"), links.get("project"))
        author = cls._parse_user(embedded.get("author"), links.get("author"))
        assignee = cls._parse_user(embedded.get("assignee"), links.get("assignee"))

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
            lock_version=data.get("lockVersion"),
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

    @staticmethod
    def _extract_id_from_href(href: str) -> Optional[int]:
        """Extract ID from API href like /api/v3/statuses/1"""
        if href:
            parts = href.rstrip("/").split("/")
            if parts:
                try:
                    return int(parts[-1])
                except (ValueError, IndexError):
                    pass
        return None

    @classmethod
    def _parse_status(
        cls, embedded_data: Optional[Dict], link_data: Optional[Dict]
    ) -> Optional[Status]:
        """Parse status from embedded data or link."""
        if embedded_data:
            return Status.from_hal_json(embedded_data)
        elif link_data:
            if status_id := cls._extract_id_from_href(link_data.get("href", "")):
                return Status(
                    id=status_id,
                    name=link_data.get("title", f"Status {status_id}"),
                    color=None,
                )
        return None

    @classmethod
    def _parse_type(
        cls, embedded_data: Optional[Dict], link_data: Optional[Dict]
    ) -> Optional[Type]:
        """Parse type from embedded data or link."""
        if embedded_data:
            return Type.from_hal_json(embedded_data)
        elif link_data:
            if type_id := cls._extract_id_from_href(link_data.get("href", "")):
                return Type(
                    id=type_id,
                    name=link_data.get("title", f"Type {type_id}"),
                    color=None,
                )
        return None

    @classmethod
    def _parse_priority(
        cls, embedded_data: Optional[Dict], link_data: Optional[Dict]
    ) -> Optional[Priority]:
        """Parse priority from embedded data or link."""
        if embedded_data:
            return Priority.from_hal_json(embedded_data)
        elif link_data:
            if priority_id := cls._extract_id_from_href(link_data.get("href", "")):
                return Priority(
                    id=priority_id,
                    name=link_data.get("title", f"Priority {priority_id}"),
                )
        return None

    @classmethod
    def _parse_project(
        cls, embedded_data: Optional[Dict], link_data: Optional[Dict]
    ) -> Optional[Project]:
        """Parse project from embedded data or link."""
        if embedded_data:
            return Project.from_hal_json(embedded_data)
        elif link_data:
            if project_id := cls._extract_id_from_href(link_data.get("href", "")):
                return Project(
                    id=project_id,
                    identifier="",  # Not available in link
                    name=link_data.get("title", f"Project {project_id}"),
                )
        return None

    @classmethod
    def _parse_user(
        cls, embedded_data: Optional[Dict], link_data: Optional[Dict]
    ) -> Optional[User]:
        """Parse user from embedded data or link."""
        if embedded_data:
            return User.from_hal_json(embedded_data)
        elif link_data:
            if user_id := cls._extract_id_from_href(link_data.get("href", "")):
                return User(
                    id=user_id,
                    name=link_data.get("title", f"User {user_id}"),
                )
        return None
