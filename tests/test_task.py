import pytest
import sys
import os
from datetime import datetime, timedelta
import tempfile
from database.database_manager import DatabaseManager

# Добавляем путь к модулям проекта
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from controllers.task_controller import TaskController
from controllers.project_controller import ProjectController
from controllers.user_controller import UserController
from database.database_manager import DatabaseManager
from models.task import Task
from models.project import Project
from models.user import User

class TestTaskController:
    """Тесты для TaskController"""

    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.db_manager = DatabaseManager(self.temp_db.name)
        self.db_manager.create_tables()
        self.controller = TaskController(self.db_manager)

        # Создаем тестовые проекты и пользователей
        self.project_id = self.db_manager.add_project(
            Project("Тестовый проект", "Описание проекта", datetime.now(), datetime.now() + timedelta(days=30))
        )
        self.user_id = self.db_manager.add_user(
            User("test_user", "test@example.com", "developer")
        )

    def teardown_method(self):
        self.db_manager.close()
        os.unlink(self.temp_db.name)

    def test_add_task(self):
        """Тест добавления задачи"""
        task_id = self.controller.add_task(
            "Тестовая задача",
            "Описание тестовой задачи",
            1,
            datetime.now() + timedelta(days=7),
            self.project_id,
            self.user_id
        )

        assert task_id is not None
        assert isinstance(task_id, int)

        # Проверяем, что задача действительно добавлена
        task = self.controller.get_task(task_id)
        assert task.title == "Тестовая задача"
        assert task.description == "Описание тестовой задачи"
        assert task.priority == 1

    def test_get_task(self):
        """Тест получения задачи по ID"""
        task_id = self.controller.add_task(
            "Задача для получения",
            "Описание",
            2,
            datetime.now() + timedelta(days=5),
            self.project_id,
            self.user_id
        )

        task = self.controller.get_task(task_id)
        assert task is not None
        assert task.title == "Задача для получения"
        assert task.status == "pending"

    def test_get_all_tasks(self):
        """Тест получения всех задач"""
        # Добавляем несколько задач
        self.controller.add_task("Задача 1", "Описание 1", 1, datetime.now() + timedelta(days=1), self.project_id,
                                 self.user_id)
        self.controller.add_task("Задача 2", "Описание 2", 2, datetime.now() + timedelta(days=2), self.project_id,
                                 self.user_id)

        tasks = self.controller.get_all_tasks()
        assert len(tasks) >= 2

        # Проверяем, что все задачи имеют необходимые атрибуты
        for task in tasks:
            assert hasattr(task, "id")
            assert hasattr(task, "title")
            assert hasattr(task, "status")

    def test_update_task(self):
        """Тест обновления задачи"""
        task_id = self.controller.add_task(
            "Старое название",
            "Старое описание",
            1,
            datetime.now() + timedelta(days=3),
            self.project_id,
            self.user_id
        )

        # Обновляем задачу
        self.controller.update_task(
            task_id,
            title="Новое название",
            description="Новое описание",
            priority=3
        )

        # Проверяем изменения
        task = self.controller.get_task(task_id)
        assert task.title == "Новое название"
        assert task.description == "Новое описание"
        assert task.priority == 3

    def test_delete_task(self):
        """Тест удаления задачи"""
        task_id = self.controller.add_task(
            "Задача для удаления",
            "Описание",
            1,
            datetime.now() + timedelta(days=1),
            self.project_id,
            self.user_id
        )

        # Удаляем задачу
        self.controller.delete_task(task_id)

        # Проверяем, что задача удалена
        task = self.controller.get_task(task_id)
        assert task is None

    def test_search_tasks(self):
        """Тест поиска задач"""
        self.controller.add_task("Важная задача", "Срочное выполнение", 1, datetime.now() + timedelta(days=1),
                                 self.project_id, self.user_id)
        self.controller.add_task("Обычная задача", "Плановое выполнение", 2, datetime.now() + timedelta(days=2),
                                 self.project_id, self.user_id)

        # Поиск по названию
        results = self.controller.search_tasks("Важная")
        assert len(results) >= 1

        # Поиск по описанию
        results = self.controller.search_tasks("Срочное")
        assert len(results) >= 1

    def test_update_task_status(self):
        """Тест обновления статуса задачи"""
        task_id = self.controller.add_task(
            "Задача для смены статуса",
            "Описание",
            1,
            datetime.now() + timedelta(days=1),
            self.project_id,
            self.user_id
        )

        # Обновляем статус
        self.controller.update_task_status(task_id, "in_progress")

        # Проверяем изменения
        task = self.controller.get_task(task_id)
        assert task.status == "in_progress"

        # Обновляем на завершенный
        self.controller.update_task_status(task_id, "completed")
        task = self.controller.get_task(task_id)
        assert task.status == "completed"

    def test_get_overdue_tasks(self):
        """Тест получения просроченных задач"""
        # Создаем просроченную задачу
        task_id = self.controller.add_task(
            "Просроченная задача",
            "Описание",
            1,
            datetime.now() - timedelta(days=1),  # Вчерашний срок
            self.project_id,
            self.user_id
        )

        overdue_tasks = self.controller.get_overdue_tasks()
        assert len(overdue_tasks) >= 1

        for task in overdue_tasks:
            assert task.is_overdue() == True

    def test_get_tasks_by_project(self):
        """Тест получения задач проекта"""
        # Создаем второй проект
        project2_id = self.db_manager.add_project(
            Project("Второй проект", "Описание", datetime.now(), datetime.now() + timedelta(days=30))
        )

        # Добавляем задачи в разные проекты
        self.controller.add_task("Задача в проекте 1", "Описание", 1, datetime.now() + timedelta(days=1),
                                 self.project_id, self.user_id)
        self.controller.add_task("Задача в проекте 2", "Описание", 1, datetime.now() + timedelta(days=1), project2_id,
                                 self.user_id)

        tasks = self.controller.get_tasks_by_project(self.project_id)
        assert len(tasks) >= 1

        for task in tasks:
            assert task.project_id == self.project_id

    def test_get_tasks_by_user(self):
        """Тест получения задач пользователя"""
        # Создаем второго пользователя
        user2_id = self.db_manager.add_user(
            User("user2", "user2@example.com", "developer")
        )

        # Добавляем задачи разным пользователям
        self.controller.add_task("Задача пользователя 1", "Описание", 1, datetime.now() + timedelta(days=1),
                                 self.project_id, self.user_id)
        self.controller.add_task("Задача пользователя 2", "Описание", 1, datetime.now() + timedelta(days=1),
                                 self.project_id, user2_id)

        tasks = self.controller.get_tasks_by_user(self.user_id)
        assert len(tasks) >= 1

        for task in tasks:
            assert task.assignee_id == self.user_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])