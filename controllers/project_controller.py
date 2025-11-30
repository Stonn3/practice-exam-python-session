from datetime import datetime
from models.project import Project


def _coerce_id(v):
    return getattr(v, "id", v)


class _IntId(int):
    def __new__(cls, value: int):
        obj = int.__new__(cls, int(value))
        obj.id = int(value)
        return obj


def _ensure_dt(v):
    return v if isinstance(v, datetime) else datetime.fromisoformat(v)


class ProjectController:
    def __init__(self, db_manager):
        self.db = db_manager

    def add_project(self, name, description, start_date, end_date):
        p = Project(name, description, start_date, end_date)
        p.id = self.db.add_project(p)
        return _IntId(p.id)  # int-like с .id

    def get_project(self, project_id):
        project_id = _coerce_id(project_id)
        r = self.db.get_project_by_id(project_id)
        if not r:
            return None
        p = Project(r["name"], r["description"], _ensure_dt(r["start_date"]), _ensure_dt(r["end_date"]))
        p.id = r["id"]; p.status = r["status"]
        return p

    def update_project(self, project_id, **kwargs):
        project_id = _coerce_id(project_id)
        # допускаем строки дат
        if "start_date" in kwargs and isinstance(kwargs["start_date"], str):
            kwargs["start_date"] = datetime.fromisoformat(kwargs["start_date"])
        if "end_date" in kwargs and isinstance(kwargs["end_date"], str):
            kwargs["end_date"] = datetime.fromisoformat(kwargs["end_date"])
        return self.db.update_project(project_id, **kwargs)

    def get_all_projects(self):
        res = []
        for r in self.db.get_all_projects():
            p = Project(r["name"], r["description"], _ensure_dt(r["start_date"]), _ensure_dt(r["end_date"]))
            p.id = r["id"]; p.status = r["status"]
            res.append(p)
        return res

    

    def delete_project(self, project_id):
        project_id = _coerce_id(project_id)
        return self.db.delete_project(project_id) > 0


    def get_project_progress(self, project_id):
        project_id = _coerce_id(project_id)
        tasks = self.db.get_tasks_by_project(project_id)
        if tasks:
            total = len(tasks)
            done = sum(1 for t in tasks if t["status"] == "completed")
            return float(done * 100.0 / total)
        p = self.get_project(project_id)
        return float(p.get_progress()) if p else 0.0

    def update_project_status(self, project_id, new_status):
        p = self.get_project(project_id)
        if p is None:
            return None
        p.update_status(new_status)
        self.db.update_project(p.id, status=p.status)
        return self.get_project(p.id)
