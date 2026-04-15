import sqlite3
import hashlib
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from pathlib import Path
from datetime import datetime

APP_DIR = Path.home() / ".checklist_drive_app"
APP_DIR.mkdir(exist_ok=True)
CONFIG_FILE = APP_DIR / "config.txt"


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class DatabaseManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        cur = self.conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS checklist_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0,
                position INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (note_id) REFERENCES notes(id)
            )
            """
        )

        self.conn.commit()

    def create_user(self, username: str, password: str):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
            (username.strip(), hash_password(password), datetime.now().isoformat())
        )
        self.conn.commit()

    def authenticate(self, username: str, password: str):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM users WHERE username = ? AND password_hash = ?",
            (username.strip(), hash_password(password))
        )
        return cur.fetchone()

    def list_notes(self, user_id: int):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM notes WHERE user_id = ? ORDER BY updated_at DESC",
            (user_id,)
        )
        return cur.fetchall()

    def create_note(self, user_id: int, title: str):
        now = datetime.now().isoformat()
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO notes (user_id, title, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (user_id, title.strip(), now, now)
        )
        self.conn.commit()
        return cur.lastrowid

    def update_note_title(self, note_id: int, title: str):
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE notes SET title = ?, updated_at = ? WHERE id = ?",
            (title.strip(), datetime.now().isoformat(), note_id)
        )
        self.conn.commit()

    def delete_note(self, note_id: int):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM checklist_items WHERE note_id = ?", (note_id,))
        cur.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        self.conn.commit()

    def get_note_items(self, note_id: int):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM checklist_items WHERE note_id = ? ORDER BY position, id",
            (note_id,)
        )
        return cur.fetchall()

    def add_item(self, note_id: int, text: str):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT COALESCE(MAX(position), -1) + 1 FROM checklist_items WHERE note_id = ?",
            (note_id,)
        )
        next_position = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO checklist_items (note_id, text, done, position) VALUES (?, ?, 0, ?)",
            (note_id, text.strip(), next_position)
        )
        cur.execute(
            "UPDATE notes SET updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), note_id)
        )
        self.conn.commit()

    def update_item_status(self, item_id: int, done: int, note_id: int):
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE checklist_items SET done = ? WHERE id = ?",
            (done, item_id)
        )
        cur.execute(
            "UPDATE notes SET updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), note_id)
        )
        self.conn.commit()

    def update_item_text(self, item_id: int, text: str, note_id: int):
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE checklist_items SET text = ? WHERE id = ?",
            (text.strip(), item_id)
        )
        cur.execute(
            "UPDATE notes SET updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), note_id)
        )
        self.conn.commit()

    def delete_item(self, item_id: int, note_id: int):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM checklist_items WHERE id = ?", (item_id,))
        cur.execute(
            "UPDATE notes SET updated_at = ? WHERE id = ?",
            (datetime.now().isoformat(), note_id)
        )
        self.conn.commit()


class LoginWindow(ttk.Frame):
    def __init__(self, master, on_login_success):
        super().__init__(master, padding=20)
        self.master = master
        self.on_login_success = on_login_success
        self.db = None
        self.build_ui()

    def build_ui(self):
        self.pack(fill="both", expand=True)

        title = ttk.Label(self, text="Checklist com Login", font=("Segoe UI", 16, "bold"))
        title.pack(pady=(0, 15))

        drive_frame = ttk.LabelFrame(self, text="Banco de dados")
        drive_frame.pack(fill="x", pady=(0, 15))

        self.db_path_var = tk.StringVar(value=self.load_saved_db_path())
        ttk.Entry(drive_frame, textvariable=self.db_path_var).pack(side="left", fill="x", expand=True, padx=8, pady=8)
        ttk.Button(drive_frame, text="Escolher", command=self.choose_db_path).pack(side="left", padx=(0, 8), pady=8)
        ttk.Button(drive_frame, text="Conectar", command=self.connect_database).pack(side="left", padx=(0, 8), pady=8)

        form = ttk.LabelFrame(self, text="Acesso")
        form.pack(fill="x")

        ttk.Label(form, text="Usuário").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        self.username_entry = ttk.Entry(form)
        self.username_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        ttk.Label(form, text="Senha").grid(row=2, column=0, sticky="w", padx=10, pady=(0, 5))
        self.password_entry = ttk.Entry(form, show="*")
        self.password_entry.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))

        form.columnconfigure(0, weight=1)

        buttons = ttk.Frame(form)
        buttons.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 10))
        ttk.Button(buttons, text="Entrar", command=self.login).pack(side="left")
        ttk.Button(buttons, text="Criar conta", command=self.register).pack(side="left", padx=8)

        self.status_var = tk.StringVar(value="Escolha ou confirme o arquivo .db na sua pasta do Google Drive.")
        ttk.Label(self, textvariable=self.status_var).pack(anchor="w", pady=(10, 0))

        self.password_entry.bind("<Return>", lambda e: self.login())
        self.username_entry.focus()

    def choose_db_path(self):
        file_path = filedialog.asksaveasfilename(
            title="Escolha o banco SQLite",
            defaultextension=".db",
            filetypes=[("Banco SQLite", "*.db")],
            initialfile="checklist_drive.db"
        )
        if file_path:
            self.db_path_var.set(file_path)

    def save_db_path(self, path: str):
        CONFIG_FILE.write_text(path, encoding="utf-8")

    def load_saved_db_path(self) -> str:
        if CONFIG_FILE.exists():
            return CONFIG_FILE.read_text(encoding="utf-8").strip()
        return ""

    def connect_database(self):
        db_path = self.db_path_var.get().strip()
        if not db_path:
            messagebox.showwarning("Aviso", "Escolha um arquivo .db primeiro.")
            return

        try:
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            self.db = DatabaseManager(Path(db_path))
            self.save_db_path(db_path)
            self.status_var.set(f"Banco conectado: {db_path}")
            messagebox.showinfo("Sucesso", "Banco conectado com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível conectar ao banco.\n\n{e}")

    def ensure_db(self):
        if self.db is None:
            self.connect_database()
        return self.db is not None

    def login(self):
        if not self.ensure_db():
            return

        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Aviso", "Preencha usuário e senha.")
            return

        user = self.db.authenticate(username, password)
        if not user:
            messagebox.showerror("Erro", "Usuário ou senha inválidos.")
            return

        self.on_login_success(self.db, user)

    def register(self):
        if not self.ensure_db():
            return

        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if len(username) < 3:
            messagebox.showwarning("Aviso", "O usuário precisa ter pelo menos 3 caracteres.")
            return

        if len(password) < 4:
            messagebox.showwarning("Aviso", "A senha precisa ter pelo menos 4 caracteres.")
            return

        try:
            self.db.create_user(username, password)
            messagebox.showinfo("Conta criada", "Usuário criado com sucesso. Agora é só entrar.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Esse nome de usuário já existe.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao criar usuário.\n\n{e}")


class MainWindow(ttk.Frame):
    def __init__(self, master, db: DatabaseManager, user):
        super().__init__(master, padding=12)
        self.master = master
        self.db = db
        self.user = user
        self.selected_note_id = None
        self.build_ui()
        self.load_notes()

    def build_ui(self):
        self.pack(fill="both", expand=True)

        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 10))

        ttk.Label(
            header,
            text=f"Olá, {self.user['username']}!",
            font=("Segoe UI", 15, "bold")
        ).pack(side="left")

        ttk.Button(header, text="Nova lista", command=self.create_note).pack(side="right")

        body = ttk.PanedWindow(self, orient="horizontal")
        body.pack(fill="both", expand=True)

        left = ttk.Frame(body, padding=8)
        right = ttk.Frame(body, padding=8)
        body.add(left, weight=1)
        body.add(right, weight=3)

        ttk.Label(left, text="Minhas listas", font=("Segoe UI", 11, "bold")).pack(anchor="w")

        self.notes_listbox = tk.Listbox(left, height=20)
        self.notes_listbox.pack(fill="both", expand=True, pady=8)
        self.notes_listbox.bind("<<ListboxSelect>>", self.on_select_note)

        left_buttons = ttk.Frame(left)
        left_buttons.pack(fill="x")
        ttk.Button(left_buttons, text="Renomear", command=self.rename_note).pack(side="left")
        ttk.Button(left_buttons, text="Excluir", command=self.delete_note).pack(side="left", padx=8)

        self.note_title_var = tk.StringVar(value="Selecione uma lista")
        ttk.Label(right, textvariable=self.note_title_var, font=("Segoe UI", 12, "bold")).pack(anchor="w")

        add_frame = ttk.Frame(right)
        add_frame.pack(fill="x", pady=8)

        self.new_item_entry = ttk.Entry(add_frame)
        self.new_item_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(add_frame, text="Adicionar item", command=self.add_item).pack(side="left", padx=(8, 0))
        self.new_item_entry.bind("<Return>", lambda e: self.add_item())

        self.canvas = tk.Canvas(right, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(right, orient="vertical", command=self.canvas.yview)
        self.items_frame = ttk.Frame(self.canvas)

        self.items_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.items_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def load_notes(self):
        self.notes = self.db.list_notes(self.user["id"])
        self.notes_listbox.delete(0, tk.END)
        for note in self.notes:
            self.notes_listbox.insert(tk.END, note["title"])

    def create_note(self):
        title = simpledialog.askstring("Nova lista", "Título da lista:", parent=self)
        if not title:
            return
        self.db.create_note(self.user["id"], title)
        self.load_notes()

    def get_selected_note(self):
        selection = self.notes_listbox.curselection()
        if not selection:
            return None
        return self.notes[selection[0]]

    def on_select_note(self, event=None):
        note = self.get_selected_note()
        if not note:
            return
        self.selected_note_id = note["id"]
        self.note_title_var.set(note["title"])
        self.render_items()

    def rename_note(self):
        note = self.get_selected_note()
        if not note:
            messagebox.showwarning("Aviso", "Selecione uma lista.")
            return
        title = simpledialog.askstring("Renomear lista", "Novo título:", initialvalue=note["title"], parent=self)
        if not title:
            return
        self.db.update_note_title(note["id"], title)
        self.load_notes()
        self.note_title_var.set(title)

    def delete_note(self):
        note = self.get_selected_note()
        if not note:
            messagebox.showwarning("Aviso", "Selecione uma lista.")
            return
        if not messagebox.askyesno("Confirmar", f"Excluir a lista '{note['title']}'?"):
            return
        self.db.delete_note(note["id"])
        self.selected_note_id = None
        self.note_title_var.set("Selecione uma lista")
        self.clear_items()
        self.load_notes()

    def add_item(self):
        if not self.selected_note_id:
            messagebox.showwarning("Aviso", "Selecione uma lista primeiro.")
            return
        text = self.new_item_entry.get().strip()
        if not text:
            return
        self.db.add_item(self.selected_note_id, text)
        self.new_item_entry.delete(0, tk.END)
        self.render_items()
        self.load_notes()

    def clear_items(self):
        for widget in self.items_frame.winfo_children():
            widget.destroy()

    def render_items(self):
        self.clear_items()
        if not self.selected_note_id:
            return

        items = self.db.get_note_items(self.selected_note_id)

        for item in items:
            row = ttk.Frame(self.items_frame)
            row.pack(fill="x", pady=3)

            done_var = tk.IntVar(value=item["done"])
            chk = ttk.Checkbutton(
                row,
                variable=done_var,
                command=lambda i=item, v=done_var: self.toggle_item(i["id"], v.get())
            )
            chk.pack(side="left")

            text_var = tk.StringVar(value=item["text"])
            ent = ttk.Entry(row, textvariable=text_var)
            ent.pack(side="left", fill="x", expand=True, padx=6)
            ent.bind("<FocusOut>", lambda e, i=item, v=text_var: self.save_item_text(i["id"], v.get()))
            ent.bind("<Return>", lambda e: self.master.focus())

            ttk.Button(row, text="Excluir", command=lambda i=item: self.remove_item(i["id"])).pack(side="left", padx=(6, 0))

    def toggle_item(self, item_id: int, done: int):
        self.db.update_item_status(item_id, done, self.selected_note_id)
        self.load_notes()

    def save_item_text(self, item_id: int, text: str):
        if not text.strip():
            return
        self.db.update_item_text(item_id, text, self.selected_note_id)
        self.load_notes()

    def remove_item(self, item_id: int):
        self.db.delete_item(item_id, self.selected_note_id)
        self.render_items()
        self.load_notes()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Checklist Drive")
        self.geometry("900x560")
        self.minsize(760, 480)
        self.show_login()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_window()
        LoginWindow(self, self.show_main)

    def show_main(self, db, user):
        self.clear_window()
        MainWindow(self, db, user)


if __name__ == "__main__":
    app = App()
    app.mainloop()
