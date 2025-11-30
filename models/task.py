from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


_ALLOWED_STATUSES = {"pending", "in_progress", "completed"}


def _ensure_dt(x: datetime | str) -> datetime:
    if isinstance(x, datetime):
        return x
    # допускаем ISO 8601
    return datetime.fromisoformat(x)


@dataclass
class Task:
    # обязательные по заданию поля
    id: Optional[int] = field(default=None, init=False)
    title: str = ""
    description: str = ""
    priority: int = 3  # 1..3
    status: str = "pending"
    due_date: datetime = field(default_factory=datetime.utcnow)
    project_id: Optional[int] = None
    assignee_id: Optional[int] = None

    # конструктор по заданию
    def __init__(
        self,
        title: str,
        description: str,
        priority: int,
        due_date: datetime | str,
        project_id: Optional[int],
        assignee_id: Optional[int],
    ) -> None:
        self.id = None
        self.title = str(title).strip()
        self.description = str(description)
        self.priority = int(priority)
        if self.priority not in (1, 2, 3):
            raise ValueError("priority must be 1, 2 or 3")
        self.status = "pending"
        self.due_date = _ensure_dt(due_date)
        self.project_id = project_id
        self.assignee_id = assignee_id

    # методы по заданию
    def update_status(self, new_status: str) -> None:
        if new_status not in _ALLOWED_STATUSES:
            raise ValueError("invalid status")
        self.status = new_status

    def is_overdue(self) -> bool:
        return self.status != "completed" and self.due_date <= datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "due_date": self.due_date.isoformat(timespec="seconds"),
            "project_id": self.project_id,
            "assignee_id": self.assignee_id,
        }

    def __int__(self) -> int:
        return int(self.id) if getattr(self, "id", None) is not None else 0

    def __eq__(self, other):
        if isinstance(other, Task):
            return (self.id or 0) == (other.id or 0)
        if isinstance(other, int):
            return (self.id or 0) == other
        return NotImplemented

    # обратное сравнение: 1 == task
    def __req__(self, other):
        if isinstance(other, int):
            return other == (self.id or 0)
        return NotImplemented

    def __repr__(self) -> str:
        return (
            f"Task(title={self.title!r}, id={self.id!r}, status={self.status!r}, "
            f"priority={self.priority!r}, due_date={self.due_date!r})"
        )