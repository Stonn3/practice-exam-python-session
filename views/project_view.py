import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


class ProjectView:
    def __init__(self, parent, project_controller, task_controller):
        self.ctrl = project_controller
        self.task_ctrl = task_controller

        self.frame = parent
        self._build_form()
        self._build_table()
        self.refresh_table()

    def _build_form(self):
        frm = ttk.LabelFrame(self.frame, text="Проект")
        frm.pack(fill=tk.X, padx=10, pady=6)

        self.name_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        self.start_var = tk.StringVar()
        self.end_var = tk.StringVar()

        grid = ttk.Frame(frm)
        grid.pack(fill=tk.X, padx=6, pady=6)

        ttk.Label(grid, text="Название").grid(row=0, column=0, sticky="w")
        ttk.Entry(grid, textvariable=self.name_var, width=35).grid(row=0, column=1, sticky="w")
        ttk.Label(grid, text="Описание").grid(row=1, column=0, sticky="w")
        ttk.Entry(grid, textvariable=self.desc_var, width=60).grid(row=1, column=1, sticky="w")
        ttk.Label(grid, text="Начало (YYYY-MM-DD)").grid(row=2, column=0, sticky="w")
        ttk.Entry(grid, textvariable=self.start_var, width=20).grid(row=2, column=1, sticky="w")
        ttk.Label(grid, text="Окончание (YYYY-MM-DD)").grid(row=3, column=0, sticky="w")
        ttk.Entry(grid, textvariable=self.end_var, width=20).grid(row=3, column=1, sticky="w")

        btns = ttk.Frame(frm)
        btns.pack(fill=tk.X, padx=6, pady=6)
        ttk.Button(btns, text="Добавить", command=self._on_add).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Обновить", command=self._on_update).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Удалить", command=self._on_delete).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Прогресс", command=self._on_progress).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Задачи проекта", command=self._on_show_tasks).pack(side=tk.LEFT, padx=2)

    def _build_table(self):
        tbl = ttk.Frame(self.frame)
        tbl.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        cols = ("id", "name", "status", "start_date", "end_date")
        self.tree = ttk.Treeview(tbl, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, stretch=True, width=150)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return int(self.tree.item(sel[0])["values"][0])

    def _parse_date(self, s):
        return datetime.fromisoformat(s.strip())

    def _reload(self, items):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for p in items:
            self.tree.insert("", tk.END, values=(
                p.id, p.name, p.status,
                p.start_date.date().isoformat(),
                p.end_date.date().isoformat()
            ))

    def refresh_table(self):
        self._reload(self.ctrl.get_all_projects())

    def _on_add(self):
        try:
            p = self.ctrl.add_project(
                self.name_var.get(),
                self.desc_var.get(),
                self._parse_date(self.start_var.get()),
                self._parse_date(self.end_var.get()),
            )
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _on_update(self):
        pid = self._selected_id()
        if not pid:
            return
        try:
            self.ctrl.update_project(
                pid,
                name=self.name_var.get(),
                description=self.desc_var.get(),
                start_date=self._parse_date(self.start_var.get()),
                end_date=self._parse_date(self.end_var.get()),
            )
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _on_delete(self):
        pid = self._selected_id()
        if not pid:
            return
        if self.ctrl.delete_project(pid):
            self.refresh_table()

    def _on_progress(self):
        pid = self._selected_id()
        if not pid:
            return
        try:
            pct = self.ctrl.get_project_progress(pid)
            messagebox.showinfo("Прогресс проекта", f"{pct}%")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _on_show_tasks(self):
        pid = self._selected_id()
        if not pid:
            return
        tasks = self.task_ctrl.get_tasks_by_project(pid)
        text = "\n".join(f"[{t.id}] {t.title} - {t.status}" for t in tasks) or "(нет задач)"
        messagebox.showinfo("Задачи проекта", text)