import pytest
from datetime import datetime, timedelta

from models.task import Task
from models.project import Project
from models.user import User


class TestTaskModel:
    def test_create_and_to_dict(self):
        due = datetime.now() + timedelta(days=1)
        t = Task("Title", "Desc", 2, due, project_id=1, assignee_id=2)
        d = t.to_dict()
        assert d["title"] == "Title"
        assert d["priority"] == 2
        assert d["status"] == "pending"
        assert "due_date" in d

    def test_priority_validation(self):
        due = datetime.now() + timedelta(days=1)
        with pytest.raises(ValueError):
            Task("T", "D", 5, due, None, None)

    def test_update_status_validation(self):
        due = datetime.now() + timedelta(days=1)
        t = Task("T", "D", 1, due, None, None)
        with pytest.raises(ValueError):
            t.update_status("bad")

    def test_is_overdue(self):
        due = datetime.now() - timedelta(hours=1)
        t = Task("T", "D", 1, due, None, None)
        assert t.is_overdue() is True
        t.update_status("completed")
   


class TestProjectModel:
    def test_create_and_progress(self):
        start = datetime.now() - timedelta(days=1)
        end = datetime.now() + timedelta(days=1)
        p = Project("Name", "Desc", start, end)
        assert p.status == "active"
        assert 0 <= p.get_progress() <= 100

    def test_update_status_validation(self):
        start = datetime(2024, 1, 1)
        end = datetime(2024, 2, 1)
        p = Project("P", "", start, end)
        with pytest.raises(ValueError):
            p.update_status("bad")

    def test_dates_validation(self):
        start = datetime(2024, 1, 10)
        end = datetime(2024, 1, 5)
        with pytest.raises(ValueError):
            Project("P", "", start, end)

    


class TestUserModel:
    def test_create_and_to_dict(self):
        u = User("name", "a@b.com", "developer")
        d = u.to_dict()
        assert d["username"] == "name"
        assert d["role"] == "developer"
        assert "registration_date" in d

    def test_email_and_role_validation(self):
        with pytest.raises(ValueError):
            User("n", "badmail", "developer")
        with pytest.raises(ValueError):
            User("n", "a@b.com", "badrole")

    def test_update_info(self):
        u = User("name", "a@b.com", "developer")
        u.update_info(username="nn", email="x@y.z", role="manager")
        assert u.username == "nn"
       