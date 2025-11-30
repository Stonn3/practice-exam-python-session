import tempfile
import os
from datetime import datetime, timedelta

from models.task import Task
from models.project import Project
from database.database_manager import DatabaseManager
from models.user import User


class TestDatabase:
    def setup_method(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db = DatabaseManager(self.temp_db.name)
        self.db.create_user_table()
        self.db.create_project_table()
        self.db.create_task_table()

    def teardown_method(self):
        self.db.close()
        os.unlink(self.temp_db.name)

    def test_user_crud(self):
        u = User("u", "u@a.b", "developer")
        uid = self.db.add_user(u)
        row = self.db.get_user_by_id(uid)
        assert row["username"] == "u"
        assert self.db.update_user(uid, role="manager") == 1
        row2 = self.db.get_user_by_id(uid)
        assert row2["role"] == "manager"
        assert self.db.delete_user(uid) == 1
        assert self.db.get_user_by_id(uid) is None

    def test_project_crud(self):
        p = Project("p", "", datetime(2024,1,1), datetime(2024,2,1))
        pid = self.db.add_project(p)
        row = self.db.get_project_by_id(pid)
        assert row["name"] == "p"
        assert self.db.update_project(pid, status="on_hold") == 1
        assert self.db.get_project_by_id(pid)["status"] == "on_hold"
        assert self.db.get_all_projects()
        

    def test_task_crud_and_queries(self):
        # add user/project to reference
        uid = self.db.add_user(User("u", "u@a.b", "developer"))
        pid = self.db.add_project(Project("p", "", datetime(2024,1,1), datetime(2024,2,1)))
        due = datetime.now() + timedelta(days=1)
        t = Task("t1", "desc", 1, due, pid, uid)
        tid = self.db.add_task(t)
        row = self.db.get_task_by_id(tid)
        assert row["title"] == "t1"
        assert self.db.update_task(tid, status="in_progress") == 1
        assert self.db.get_task_by_id(tid)["status"] == "in_progress"
        assert len(self.db.search_tasks("t1")) == 1
        assert len(self.db.get_tasks_by_project(pid)) == 1
        assert len(self.db.get_tasks_by_user(uid)) == 1
        assert len(self.db.get_all_tasks()) == 1