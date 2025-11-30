import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class TaskView:
    def __init__(self, parent, task_controller, project_controller, user_controller):
        self.ctrl = task_controller
        self.project_ctrl = project_controller
        self.user_ctrl = user_controller

        self.frame = parent
        self._build_form()
        self._build_table()
        self.refresh_table()

    # ---- UI ----
    def _build_form(self):
        frm = ttk.LabelFrame(self.frame, text="Добавить/Изменить задачу")
        frm.pack(fill=tk.X, padx=10, pady=6)

        self.title_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        self.priority_var = tk.StringVar(value="2")
        self.due_var = tk.StringVar()
        self.project_var = tk.StringVar()
        self.user_var = tk.StringVar()
        self.status_var = tk.StringVar(value="pending")
        self.search_var = tk.StringVar()
        self.filter_status_var = tk.StringVar(value="")
        self.filter_priority_var = tk.StringVar(value="")

        grid = ttk.Frame(frm)
        grid.pack(fill=tk.X, padx=6, pady=6)

        def add_row(r, text, var, width=25):
            ttk.Label(grid, text=text).grid(row=r, column=0, sticky="w", padx=4, pady=3)
            e = ttk.Entry(grid, textvariable=var, width=width)
            e.grid(row=r, column=1, sticky="w", padx=4, pady=3)
            return e

        add_row(0, "Название", self.title_var)
        add_row(1, "Описание", self.desc_var, 60)
        add_row(2, "Дедлайн (YYYY-MM-DD HH:MM)", self.due_var)
        add_row(3, "ID проекта", self.project_var)
        add_row(4, "ID исполнителя", self.user_var)

        ttk.Label(grid, text="Приоритет (1/2/3)").grid(row=0, column=2, sticky="w")
        ttk.Entry(grid, textvariable=self.priority_var, width=5).grid(row=0, column=3, sticky="w")

        ttk.Label(grid, text="Статус").grid(row=1, column=2, sticky="w")
        ttk.Combobox(grid, textvariable=self.status_var, values=["pending", "in_progress", "completed"], width=17)\
            .grid(row=1, column=3, sticky="w")

        btns = ttk.Frame(frm)
        btns.pack(fill=tk.X, padx=6, pady=6)
        ttk.Button(btns, text="Добавить", command=self._on_add).pack(side=tk.LEFT, padx=3)
        ttk.Button(btns, text="Обновить выделенную", command=self._on_update).pack(side=tk.LEFT, padx=3)
        ttk.Button(btns, text="Удалить выделенную", command=self._on_delete).pack(side=tk.LEFT, padx=3)

        search = ttk.Frame(frm)
        search.pack(fill=tk.X, padx=6, pady=6)
        ttk.Label(search, text="Поиск:").pack(side=tk.LEFT)
        ttk.Entry(search, textvariable=self.search_var, width=40).pack(side=tk.LEFT, padx=4)
        ttk.Button(search, text="Найти", command=self._on_search).pack(side=tk.LEFT, padx=3)
        ttk.Button(search, text="Сброс", command=self.refresh_table).pack(side=tk.LEFT, padx=3)

        filters = ttk.Frame(frm)
        filters.pack(fill=tk.X, padx=6, pady=6)
        ttk.Label(filters, text="Фильтр статус:").pack(side=tk.LEFT)
        ttk.Combobox(filters, textvariable=self.filter_status_var,
                     values=["", "pending", "in_progress", "completed"], width=18).pack(side=tk.LEFT, padx=4)
        ttk.Label(filters, text="Фильтр приоритет:").pack(side=tk.LEFT)
        ttk.Combobox(filters, textvariable=self.filter_priority_var,
                     values=["", "1", "2", "3"], width=8).pack(side=tk.LEFT, padx=4)
        ttk.Button(filters, text="Применить", command=self._apply_filters).pack(side=tk.LEFT, padx=3)

    def _build_table(self):
        tbl = ttk.Frame(self.frame)
        tbl.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        cols = ("id", "title", "priority", "status", "due_date", "project_id", "assignee_id")
        self.tree = ttk.Treeview(tbl, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, stretch=True, width=120)
        self.tree.pack(fill=tk.BOTH, expand=True)

    # ---- Helpers ----
    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return int(self.tree.item(sel[0])["values"][0])

    def _parse_due(self):
        s = self.due_var.get().strip()
        if not s:
            raise ValueError("Введите дедлайн")
        try:
            return datetime.fromisoformat(s)
        except ValueError:
            return datetime.strptime(s, "%Y-%m-%d %H:%M")

    def _reload(self, items):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for t in items:
            self.tree.insert("", tk.END, values=(
                t.id, t.title, t.priority, t.status, t.due_date.isoformat(sep=" ", timespec="minutes"),
                t.project_id, t.assignee_id
            ))

    def refresh_table(self):
        self._reload(self.ctrl.get_all_tasks())

    # ---- Actions ----
    def _on_add(self):
        try:
            t = self.ctrl.add_task(
                self.title_var.get(),
                self.desc_var.get(),
                int(self.priority_var.get()),
                self._parse_due(),
                int(self.project_var.get()) if self.project_var.get() else None,
                int(self.user_var.get()) if self.user_var.get() else None,
            )
            # можно сразу обновить статус, если выбран не "pending"
            if self.status_var.get() != "pending":
                t = self.ctrl.update_task_status(t.id, self.status_var.get())
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _on_update(self):
        task_id = self._selected_id()
        if not task_id:
            return
        try:
            kwargs = {
                "title": self.title_var.get(),
                "description": self.desc_var.get(),
                "priority": int(self.priority_var.get()),
                "due_date": self._parse_due(),
                "project_id": int(self.project_var.get()) if self.project_var.get() else None,
                "assignee_id": int(self.user_var.get()) if self.user_var.get() else None,
                "status": self.status_var.get()
            }
            self.ctrl.update_task(task_id, **kwargs)
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _on_delete(self):
        task_id = self._selected_id()
        if not task_id:
            return
        if self.ctrl.delete_task(task_id):
            self.refresh_table()

    def _on_search(self):
        q = self.search_var.get().strip()
        if not q:
            self.refresh_table()
        else:
            self._reload(self.ctrl.search_tasks(q))

    def _apply_filters(self):
        items = self.ctrl.get_all_tasks()
        s = self.filter_status_var.get()
        p = self.filter_priority_var.get()
        if s:
            items = [t for t in items if t.status == s]
        if p:
            items = [t for t in items if str(t.priority) == p]
        self._reload(items)