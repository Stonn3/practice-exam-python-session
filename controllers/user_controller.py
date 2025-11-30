from datetime import datetime
from models.user import User
from models.task import Task


def _coerce_id(v):
    return getattr(v, "id", v)


class _IntId(int):
    """int, у которого ещё есть .id"""
    def __new__(cls, value: int):
        obj = int.__new__(cls, int(value))
        obj.id = int(value)
        return obj


class UserController:
    def __init__(self, db_manager):
        self.db = db_manager

    def add_user(self, username, email, role):
        u = User(username, email, role)
        u.id = self.db.add_user(u)
        return _IntId(u.id)  # int-like с .id

    def get_user(self, user_id):
        user_id = _coerce_id(user_id)
        r = self.db.get_user_by_id(user_id)
        if not r:
            return None
        u = User(r["username"], r["email"], r["role"])
        u.id = r["id"]
        u.registration_date = datetime.fromisoformat(r["registration_date"])
        return u

    def get_all_users(self):
        res = []
        for r in self.db.get_all_users():
            u = User(r["username"], r["email"], r["role"])
            u.id = r["id"]
            u.registration_date = datetime.fromisoformat(r["registration_date"])
            res.append(u)
        return res

    def update_user(self, user_id, **kwargs):
        user_id = _coerce_id(user_id)
        return self.db.update_user(user_id, **kwargs)

    def delete_user(self, user_id):
        user_id = _coerce_id(user_id)
        return self.db.delete_user(user_id) > 0

    def get_user_tasks(self, user_id):
        """Возвращает список объектов Task пользователя"""
        user_id = _coerce_id(user_id)
        tasks = []
        for r in self.db.get_tasks_by_user(user_id):
            t = Task(
                r["title"],
                r["description"],
                r["priority"],
                datetime.fromisoformat(r["due_date"]),
                r["project_id"],
                r["assignee_id"],
            )
            t.id = r["id"]
            t.status = r["status"]
            tasks.append(t)
        return tasks