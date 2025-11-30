import tempfile
import os
from datetime import datetime, timedelta

from database.database_manager import DatabaseManager
from controllers.task_controller import TaskController
from controllers.project_controller import ProjectController
from controllers.user_controller import UserController


class TestControllers:

    def test_task_flow_and_overdue(self):
        u = self.users.add_user("dev", "d@a.b", "developer")
        p = self.projects.add_project("proj", "", datetime.now(), datetime.now() + timedelta(days=7))
        t = self.tasks.add_task("task", "desc", 1, datetime.now() + timedelta(hours=2), p.id, u.id)
        assert t.id is not None
        t2 = self.tasks.update_task_status(t.id, "in_progress")
        assert t2.status == "in_progress"
        all_tasks = self.tasks.get_all_tasks()
        assert len(all_tasks) == 1
        overdue = self.tasks.get_overdue_tasks()
        assert len(overdue) == 0
        self.tasks.update_task(t.id, due_date=datetime.now() - timedelta(hours=1))
        assert self.tasks.get_overdue_tasks()

    def teardown_method(self):
        self.db.close()
        os.unlink(self.temp_db.name)
    def setup_method(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.db = DatabaseManager(self.temp_db.name)
        self.db.create_user_table()
        self.db.create_project_table()
        self.db.create_task_table()

        self.tasks = TaskController(self.db)
        self.projects = ProjectController(self.db)
        self.users = UserController(self.db)
    

    def test_project_progress_by_tasks(self):
        u = self.users.add_user("dev", "d@a.b", "developer")
        p = self.projects.add_project("proj", "", datetime.now(), datetime.now() + timedelta(days=2))
        t1 = self.tasks.add_task("t1", "", 1, datetime.now() + timedelta(days=1), p.id, u.id)
        t2 = self.tasks.add_task("t2", "", 2, datetime.now() + timedelta(days=1), p.id, u.id)
        # 0
        assert self.projects.get_project_progress(p.id) == 0
        # 1
        self.tasks.update_task_status(t1.id, "completed")
        assert self.projects.get_project_progress(p.id) == 50
        # 2
        self.tasks.update_task_status(t2.id, "completed")
        assert self.projects.get_project_progress(p.id) == 100
