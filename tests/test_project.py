import os
import tempfile
from datetime import datetime, timedelta
from models.user import User
from database.database_manager import DatabaseManager
from controllers.project_controller import ProjectController
from models.project import Project
from controllers.task_controller import TaskController

class TestProjectController:
    """Тесты для ProjectController"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.db_manager = DatabaseManager(self.temp_db.name)
        self.db_manager.create_tables()
        self.controller = ProjectController(self.db_manager)

    def teardown_method(self):
        self.db_manager.close()
        os.unlink(self.temp_db.name)

    def test_add_project(self):
        """Тест добавления проекта"""
        project_id = self.controller.add_project(
            "Новый проект",
            "Описание нового проекта",
            datetime.now(),
            datetime.now() + timedelta(days=30)
        )

        assert project_id is not None
        assert isinstance(project_id, int)

        # Проверяем, что проект действительно добавлен
        project = self.controller.get_project(project_id)
        assert project.name == "Новый проект"
        assert project.description == "Описание нового проекта"
        assert project.status == "active"

    def test_get_project(self):
        """Тест получения проекта по ID"""
        project_id = self.controller.add_project(
            "Проект для получения",
            "Описание",
            datetime.now(),
            datetime.now() + timedelta(days=30)
        )

        project = self.controller.get_project(project_id)
        assert project is not None
        assert project.name == "Проект для получения"
        assert project.status == "active"

    def test_get_all_projects(self):
        """Тест получения всех проектов"""
        # Добавляем несколько проектов
        self.controller.add_project("Проект 1", "Описание 1", datetime.now(), datetime.now() + timedelta(days=10))
        self.controller.add_project("Проект 2", "Описание 2", datetime.now(), datetime.now() + timedelta(days=20))

        projects = self.controller.get_all_projects()
        assert len(projects) >= 2

        # Проверяем, что все проекты имеют необходимые атрибуты
        for project in projects:
            assert hasattr(project, "id")
            assert hasattr(project, "name")
            assert hasattr(project, "status")

    def test_update_project(self):
        """Тест обновления проекта"""
        project_id = self.controller.add_project(
            "Старое название",
            "Старое описание",
            datetime.now(),
            datetime.now() + timedelta(days=10)
        )

        # Обновляем проект
        self.controller.update_project(
            project_id,
            name="Новое название",
            description="Новое описание"
        )

        # Проверяем изменения
        project = self.controller.get_project(project_id)
        assert project.name == "Новое название"
        assert project.description == "Новое описание"

    def test_delete_project(self):
        """Тест удаления проекта"""
        project_id = self.controller.add_project(
            "Проект для удаления",
            "Описание",
            datetime.now(),
            datetime.now() + timedelta(days=10)
        )

        # Удаляем проект
        self.controller.delete_project(project_id)

        # Проверяем, что проект удален
        project = self.controller.get_project(project_id)
        assert project is None

    def test_update_project_status(self):
        """Тест обновления статуса проекта"""
        project_id = self.controller.add_project(
            "Проект для смены статуса",
            "Описание",
            datetime.now(),
            datetime.now() + timedelta(days=10)
        )

        # Обновляем статус
        self.controller.update_project_status(project_id, "completed")

        # Проверяем изменения
        project = self.controller.get_project(project_id)
        assert project.status == "completed"

    def test_get_project_progress(self):
        """Тест получения прогресса проекта"""
        project_id = self.controller.add_project(
            "Проект для прогресса",
            "Описание",
            datetime.now(),
            datetime.now() + timedelta(days=10)
        )

        # Создаем задачи для проекта
        task_controller = TaskController(self.db_manager)
        user_id = self.db_manager.add_user(User("test", "test@example.com", "developer"))

        # Добавляем задачи с разными статусами
        task_controller.add_task("Задача 1", "Описание", 1, datetime.now() + timedelta(days=1), project_id, user_id)
        task_controller.add_task("Задача 2", "Описание", 1, datetime.now() + timedelta(days=1), project_id, user_id)

        # Помечаем одну задачу как выполненную
        tasks = task_controller.get_tasks_by_project(project_id)
        if tasks:
            task_controller.update_task_status(tasks[0].id, "completed")

        progress = self.controller.get_project_progress(project_id)
        assert isinstance(progress, float)
        assert 0 <= progress <= 100
        