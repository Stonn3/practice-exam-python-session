import tkinter as tk
from tkinter import ttk, messagebox
from views.task_view import TaskView
from views.project_view import ProjectView
from views.user_view import UserView
from controllers.task_controller import TaskController
from controllers.project_controller import ProjectController
from controllers.user_controller import UserController



class MainWindow(tk.Tk):
    def __init__(self, task_controller: TaskController,
                 project_controller: ProjectController,
                 user_controller: UserController):
        super().__init__()
        self.title("Task System (MVC + SQLite)")
        self.geometry("1000x650")

        self.task_controller = task_controller
        self.project_controller = project_controller
        self.user_controller = user_controller

        self._build_menu()
        self._build_tabs()

    def _build_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menubar)

    def _build_tabs(self):
        nb = ttk.Notebook(self)
        nb.pack(fill=tk.BOTH, expand=True)

        task_frame = ttk.Frame(nb)
        project_frame = ttk.Frame(nb)
        user_frame = ttk.Frame(nb)

        nb.add(task_frame, text="Задачи")
        nb.add(project_frame, text="Проекты")
        nb.add(user_frame, text="Пользователи")

        TaskView(task_frame, self.task_controller, self.project_controller, self.user_controller)
        ProjectView(project_frame, self.project_controller, self.task_controller)
        UserView(user_frame, self.user_controller, self.task_controller)