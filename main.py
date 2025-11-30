#!/usr/bin/env python3
"""
Главный файл приложения "Система управления библиотекой"
Запускает GUI приложение с использованием архитектуры MVC
"""

import os
import sys
from tkinter import messagebox

# Добавляем путь к модулям проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from controllers.task_controller import TaskController
    from controllers.project_controller import ProjectController
    from controllers.user_controller import UserController
    from database.database_manager import DatabaseManager
    from views.main_window import MainWindow
except ImportError as e:
    print(f"Ошибка импорта модулей: {e}")
    print("Убедитесь, что все файлы проекта созданы согласно заданию")
    sys.exit(1)


def main():
    """Главная функция приложения"""
    try:
        # Инициализация базы данных
        os.makedirs("database", exist_ok=True)
        db_manager = DatabaseManager("database/tasks.db")
        db_manager.create_user_table()
        db_manager.create_project_table()
        db_manager.create_task_table()

        # Инициализация контроллеров
        task_controller = TaskController(db_manager)
        project_controller = ProjectController(db_manager)
        user_controller = UserController(db_manager)

        # Создание и запуск главного окна
        root = MainWindow(task_controller, project_controller, user_controller)
        root.mainloop()

    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка запуска приложения: {e}")
        print(f"Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()