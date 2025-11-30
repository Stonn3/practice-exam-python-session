from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


_ALLOWED_PROJECT_STATUSES = {"active", "completed", "on_hold"}


def _ensure_dt(x: datetime | str) -> datetime:
    if isinstance(x, datetime):
        return x
    return datetime.fromisoformat(x)


@dataclass
class Project:
    id: Optional[int] = field(default=None, init=False)
    name: str = ""
    description: str = ""
    start_date: datetime = field(default_factory=datetime.utcnow)
    end_date: datetime = field(default_factory=datetime.utcnow)
    status: str = "active"

    def __init__(self, name: str, description: str, start_date: datetime | str, end_date: datetime | str) -> None:
        self.id = None
        self.name = str(name).strip()
        self.description = str(description)
        self.start_date = _ensure_dt(start_date)
        self.end_date = _ensure_dt(end_date)
        if self.end_date < self.start_date:
            raise ValueError("end_date must be >= start_date")
        self.status = "active"

    def update_status(self, new_status: str) -> None:
        if new_status not in _ALLOWED_PROJECT_STATUSES:
            raise ValueError("invalid project status")
        self.status = new_status

    def get_progress(self) -> int:
        """
        Временной прогресс по проекту (если нет задач).
        0% до старта, 100% после окончания, иначе доля пройденного времени.
        """
        now = datetime.utcnow()
        if now <= self.start_date:
            return 0
        if now >= self.end_date:
            return 100
        total = (self.end_date - self.start_date).total_seconds()
        done = (now - self.start_date).total_seconds()
        return max(0, min(100, int(done * 100 / total))) if total > 0 else 100

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date.isoformat(timespec="seconds"),
            "end_date": self.end_date.isoformat(timespec="seconds"),
            "status": self.status,
        }

    def __int__(self) -> int:
        return int(self.id) if getattr(self, "id", None) is not None else 0

    def __eq__(self, other):
        if isinstance(other, Project):
            return (self.id or 0) == (other.id or 0)
        if isinstance(other, int):
            return (self.id or 0) == other
        return NotImplemented

    def __req__(self, other):
        if isinstance(other, int):
            return other == (self.id or 0)
        return NotImplemented

    def __repr__(self) -> str:
        return f"Project(name={self.name!r}, id={self.id!r}, status={self.status!r})"