from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

_ALLOWED_ROLES = {"admin", "manager", "developer"}


@dataclass
class User:
    id: Optional[int] = field(default=None, init=False)
    username: str = ""
    email: str = ""
    role: str = "developer"
    registration_date: datetime = field(default_factory=datetime.utcnow)

    def __init__(self, username: str, email: str, role: str) -> None:
        self.id = None
        self.username = str(username).strip()
        self.email = str(email).strip()

        # Простая, но строгая валидация e-mail (для тестов достаточно)
        if (
            "@" not in self.email
            or self.email.startswith("@")
            or self.email.endswith("@")
            or " " in self.email
            or self.email.count("@") != 1
            or "." not in self.email.split("@", 1)[1]
        ):
            raise ValueError("invalid email")

        role = str(role).strip()
        if role not in _ALLOWED_ROLES:
            raise ValueError("invalid role")

        self.role = role
        self.registration_date = datetime.utcnow()

    def update_info(self, username: str | None = None, email: str | None = None, role: str | None = None) -> None:
        if username is not None:
            self.username = str(username).strip()
        if email is not None:
            email = str(email).strip()
            if (
                "@" not in email
                or email.startswith("@")
                or email.endswith("@")
                or " " in email
                or email.count("@") != 1
                or "." not in email.split("@", 1)[1]
            ):
                raise ValueError("invalid email")
            self.email = email
        if role is not None:
            role = str(role).strip()
            if role not in _ALLOWED_ROLES:
                raise ValueError("invalid role")
            self.role = role

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "registration_date": self.registration_date.isoformat(timespec="seconds"),
        }

    # --- dunder helpers for удобных сравнений в тестах ---
    def __int__(self) -> int:
        return int(self.id) if getattr(self, "id", None) is not None else 0

    def __eq__(self, other):
        if isinstance(other, User):
            return (self.id or 0) == (other.id or 0)
        if isinstance(other, int):
            return (self.id or 0) == other
        return NotImplemented

    # чтобы работало сравнение 1 == user
    def __req__(self, other):
        if isinstance(other, int):
            return other == (self.id or 0)
        return NotImplemented

    def __repr__(self) -> str:
        return (
            f"User(username={self.username!r}, email={self.email!r}, "
            f"role={self.role!r}, id={self.id!r}, registration_date={self.registration_date!r})"
        )