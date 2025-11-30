from __future__ import annotations

import sqlite3
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from models.task import Task
from models.project import Project
from models.user import User


def _dt_to_str(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


def _str_to_dt(s: str) -> datetime:
    # допускаем ISO 8601
    return datetime.fromisoformat(s)


class DatabaseManager:
    """
    Менеджер работы с SQLite.
    Все методы используют параметризованные запросы.
    """

    def __init__(self, db_path: str = "database/tasks.db") -> None:
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row

    # ---------- Low-level helpers ----------
    def close(self) -> None:
        try:
            self.conn.close()
        except Exception:
            pass

    def _execute(self, sql: str, params: Tuple[Any, ...] = (), commit: bool = False):
        cur = self.conn.execute(sql, params)
        if commit:
            self.conn.commit()
        return cur

    # ---------- Tables ----------
    def create_task_table(self) -> None:
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                priority INTEGER NOT NULL CHECK(priority IN (1,2,3)),
                status TEXT NOT NULL CHECK(status IN ('pending','in_progress','completed')) DEFAULT 'pending',
                due_date TEXT NOT NULL,
                project_id INTEGER NULL,
                assignee_id INTEGER NULL,
                FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE SET NULL,
                FOREIGN KEY(assignee_id) REFERENCES users(id) ON DELETE SET NULL
            )
            """,
            commit=True,
        )

    def create_project_table(self) -> None:
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('active','completed','on_hold')) DEFAULT 'active'
            )
            """,
            commit=True,
        )

    def create_user_table(self) -> None:
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin','manager','developer')),
                registration_date TEXT NOT NULL
            )
            """,
            commit=True,
        )

    # Совместимость с тестами: единый вызов создания всех таблиц
    def create_tables(self) -> None:
        # порядок важен из-за внешних ключей
        self.create_user_table()
        self.create_project_table()
        self.create_task_table()

    # ---------- Tasks CRUD ----------
    def add_task(self, task: Task) -> int:
        cur = self._execute(
            """
            INSERT INTO tasks(title, description, priority, status, due_date, project_id, assignee_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task.title,
                task.description,
                task.priority,
                task.status,
                _dt_to_str(task.due_date),
                task.project_id,
                task.assignee_id,
            ),
            commit=True,
        )
        return int(cur.lastrowid)

    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        row = self._execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return dict(row) if row else None

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        rows = self._execute("SELECT * FROM tasks ORDER BY id").fetchall()
        return [dict(r) for r in rows]

    def update_task(self, task_id: int, **kwargs) -> int:
        allowed = {"title", "description", "priority", "status", "due_date", "project_id", "assignee_id"}
        if not kwargs:
            return 0
        for k in kwargs:
            if k not in allowed:
                raise ValueError(f"invalid field for task: {k}")
        fields = []
        params: List[Any] = []
        for k, v in kwargs.items():
            if k == "due_date" and isinstance(v, datetime):
                v = _dt_to_str(v)
            fields.append(f"{k} = ?")
            params.append(v)
        params.append(task_id)
        sql = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
        cur = self._execute(sql, tuple(params), commit=True)
        return cur.rowcount

    def delete_task(self, task_id: int) -> int:
        cur = self._execute("DELETE FROM tasks WHERE id = ?", (task_id,), commit=True)
        return cur.rowcount

    def search_tasks(self, query: str) -> List[Dict[str, Any]]:
        q = f"%{query}%"
        rows = self._execute(
            "SELECT * FROM tasks WHERE title LIKE ? OR description LIKE ? ORDER BY id", (q, q)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_tasks_by_project(self, project_id: int) -> List[Dict[str, Any]]:
        rows = self._execute(
            "SELECT * FROM tasks WHERE project_id = ? ORDER BY id", (project_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    def get_tasks_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        rows = self._execute(
            "SELECT * FROM tasks WHERE assignee_id = ? ORDER BY id", (user_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    # ---------- Projects CRUD ----------
    def add_project(self, project: Project) -> int:
        cur = self._execute(
            """
            INSERT INTO projects(name, description, start_date, end_date, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                project.name,
                project.description,
                _dt_to_str(project.start_date),
                _dt_to_str(project.end_date),
                project.status,
            ),
            commit=True,
        )
        return int(cur.lastrowid)

    def get_project_by_id(self, project_id: int) -> Optional[Dict[str, Any]]:
        row = self._execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        return dict(row) if row else None

    def get_all_projects(self) -> List[Dict[str, Any]]:
        rows = self._execute("SELECT * FROM projects ORDER BY id").fetchall()
        return [dict(r) for r in rows]

    def update_project(self, project_id: int, **kwargs) -> int:
        allowed = {"name", "description", "start_date", "end_date", "status"}
        if not kwargs:
            return 0
        for k in kwargs:
            if k not in allowed:
                raise ValueError(f"invalid field for project: {k}")
        fields, params = [], []
        for k, v in kwargs.items():
            if k in {"start_date", "end_date"} and isinstance(v, datetime):
                v = _dt_to_str(v)
            fields.append(f"{k} = ?")
            params.append(v)
        params.append(project_id)
        sql = f"UPDATE projects SET {', '.join(fields)} WHERE id = ?"
        cur = self._execute(sql, tuple(params), commit=True)
        return cur.rowcount

    def delete_project(self, project_id: int) -> int:
        cur = self._execute("DELETE FROM projects WHERE id = ?", (project_id,), commit=True)
        return cur.rowcount

    # ---------- Users CRUD ----------
    def add_user(self, user: User) -> int:
        cur = self._execute(
            """
            INSERT INTO users(username, email, role, registration_date)
            VALUES (?, ?, ?, ?)
            """,
            (user.username, user.email, user.role, _dt_to_str(user.registration_date)),
            commit=True,
        )
        return int(cur.lastrowid)

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        row = self._execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None

    def get_all_users(self) -> List[Dict[str, Any]]:
        rows = self._execute("SELECT * FROM users ORDER BY id").fetchall()
        return [dict(r) for r in rows]

    def update_user(self, user_id: int, **kwargs) -> int:
        allowed = {"username", "email", "role", "registration_date"}
        if not kwargs:
            return 0
        for k in kwargs:
            if k not in allowed:
                raise ValueError(f"invalid field for user: {k}")
        fields, params = [], []
        for k, v in kwargs.items():
            if k == "registration_date" and isinstance(v, datetime):
                v = _dt_to_str(v)
            fields.append(f"{k} = ?")
            params.append(v)
        params.append(user_id)
        sql = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
        cur = self._execute(sql, tuple(params), commit=True)
        return cur.rowcount

    def delete_user(self, user_id: int) -> int:
        cur = self._execute("DELETE FROM users WHERE id = ?", (user_id,), commit=True)
        return cur.rowcount