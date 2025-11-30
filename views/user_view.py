import tkinter as tk
from tkinter import ttk, messagebox


class UserView:
    def __init__(self, parent, user_controller, task_controller):
        self.ctrl = user_controller
        self.task_ctrl = task_controller

        self.frame = parent
        self._build_form()
        self._build_table()
        self.refresh_table()

    def _build_form(self):
        frm = ttk.LabelFrame(self.frame, text="Пользователь")
        frm.pack(fill=tk.X, padx=10, pady=6)

        self.username_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.role_var = tk.StringVar(value="developer")

        grid = ttk.Frame(frm)
        grid.pack(fill=tk.X, padx=6, pady=6)

        ttk.Label(grid, text="Имя").grid(row=0, column=0, sticky="w")
        ttk.Entry(grid, textvariable=self.username_var, width=30).grid(row=0, column=1, sticky="w")

        ttk.Label(grid, text="Email").grid(row=1, column=0, sticky="w")
        ttk.Entry(grid, textvariable=self.email_var, width=35).grid(row=1, column=1, sticky="w")

        ttk.Label(grid, text="Роль").grid(row=2, column=0, sticky="w")
        ttk.Combobox(grid, textvariable=self.role_var, values=["admin", "manager", "developer"], width=20)\
            .grid(row=2, column=1, sticky="w")

        btns = ttk.Frame(frm)
        btns.pack(fill=tk.X, padx=6, pady=6)
        ttk.Button(btns, text="Добавить", command=self._on_add).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Обновить", command=self._on_update).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Удалить", command=self._on_delete).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Задачи пользователя", command=self._on_show_tasks).pack(side=tk.LEFT, padx=2)

    def _build_table(self):
        tbl = ttk.Frame(self.frame)
        tbl.pack(fill=tk.BOTH, expand=True, padx=10, pady=6)
        cols = ("id", "username", "email", "role")
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

    def _reload(self, users):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for u in users:
            self.tree.insert("", tk.END, values=(u.id, u.username, u.email, u.role))

    def refresh_table(self):
        self._reload(self.ctrl.get_all_users())

    def _on_add(self):
        try:
            self.ctrl.add_user(self.username_var.get(), self.email_var.get(), self.role_var.get())
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _on_update(self):
        uid = self._selected_id()
        if not uid:
            return
        try:
            self.ctrl.update_user(uid,
                                  username=self.username_var.get(),
                                  email=self.email_var.get(),
                                  role=self.role_var.get())
            self.refresh_table()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _on_delete(self):
        uid = self._selected_id()
        if not uid:
            return
        if self.ctrl.delete_user(uid):
            self.refresh_table()

    def _on_show_tasks(self):
        uid = self._selected_id()
        if not uid:
            return
        tasks = self.task_ctrl.get_user_tasks(uid)
        text = "\n".join(f"[{t.id}] {t.title} - {t.status}" for t in tasks) or "(нет задач)"
        messagebox.showinfo("Задачи пользователя", text)