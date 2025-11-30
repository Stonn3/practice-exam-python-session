from datetime import datetime
from models.task import Task


def _coerce_id(v):
    return getattr(v, "id", v)


class _IntId(int):
    def __new__(cls, value: int):
        obj = int.__new__(cls, int(value))
        obj.id = int(value)
        return obj


def _ensure_dt(v):
    return v if isinstance(v, datetime) else datetime.fromisoformat(v)


class TaskController:
    def __init__(self, db_manager):
        self.db = db_manager

    def add_task(self, title, description, priority, due_date, project_id, assignee_id):
        project_id = _coerce_id(project_id)
        assignee_id = _coerce_id(assignee_id)
        t = Task(title, description, int(priority), due_date, project_id, assignee_id)
        t.id = self.db.add_task(t)
        return _IntId(t.id)  # int-like с .id

    def get_task(self, task_id):
        task_id = _coerce_id(task_id)
        r = self.db.get_task_by_id(task_id)
        if not r:
            return None
        t = Task(r["title"], r["description"], r["priority"],
                 _ensure_dt(r["due_date"]), r["project_id"], r["assignee_id"])
        t.id = r["id"]
        t.status = r["status"]
        return t

    def get_all_tasks(self):
        res = []
        for r in self.db.get_all_tasks():
            t = Task(r["title"], r["description"], r["priority"],
                     _ensure_dt(r["due_date"]), r["project_id"], r["assignee_id"])
            t.id = r["id"]
            t.status = r["status"]
            res.append(t)
        return res

    def update_task(self, task_id, **kwargs):
        task_id = _coerce_id(task_id)
        # допускаем строки дат
        if "due_date" in kwargs and isinstance(kwargs["due_date"], str):
            kwargs["due_date"] = datetime.fromisoformat(kwargs["due_date"])
        return self.db.update_task(task_id, **kwargs)

    def delete_task(self, task_id):
        task_id = _coerce_id(task_id)
        return self.db.delete_task(task_id) > 0

    def search_tasks(self, query):
        # вернём объекты Task для консистентности
        items = []
        for r in self.db.search_tasks(query):
            t = Task(r["title"], r["description"], r["priority"],
                     _ensure_dt(r["due_date"]), r["project_id"], r["assignee_id"])
            t.id = r["id"]; t.status = r["status"]
            items.append(t)
        return items

    def update_task_status(self, task_id, new_status):
        t = self.get_task(task_id)
        if t is None:
            return None
        t.update_status(new_status)
        self.db.update_task(t.id, status=t.status)
        return self.get_task(t.id)

    def get_overdue_tasks(self):
        return [t for t in self.get_all_tasks() if t.is_overdue()]

    def get_tasks_by_project(self, project_id):
        project_id = _coerce_id(project_id)
        res = []
        for r in self.db.get_tasks_by_project(project_id):
            t = Task(r["title"], r["description"], r["priority"],
                     _ensure_dt(r["due_date"]), r["project_id"], r["assignee_id"])
            t.id = r["id"]; t.status = r["status"]
            res.append(t)
        return res

    def get_tasks_by_user(self, user_id):
        user_id = _coerce_id(user_id)
        res = []
        for r in self.db.get_tasks_by_user(user_id):
            t = Task(r["title"], r["description"], r["priority"],
                     _ensure_dt(r["due_date"]), r["project_id"], r["assignee_id"])
            t.id = r["id"]; t.status = r["status"]
            res.append(t)
        return res