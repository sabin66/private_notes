import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import notes

class LoginWindow(tk.Toplevel):
    def __init__(self,master,on_success):
        super().__init__(master)
        self.title("Zaloguj się")
        self.resizable(False, False)
        self.on_success = on_success

        frm = ttk.Frame(self,padding=16)
        frm.grid(sticky="nsew")

        ttk.Label(frm,text="Podaj hasło:").grid(row=0, column=0,sticky="w")
        self.var = tk.StringVar()
        self.entry = ttk.Entry(frm, textvariable=self.var, show="*", width=30)
        self.entry.grid(row=1, column=0, sticky="ew", pady=(4, 8))
        self.entry.bind("<Return>", lambda e: self.try_login())

        self.info = ttk.Label(frm, text="", foreground="red")
        self.info.grid(row=2, column=0, sticky="w")

        btns = ttk.Frame(frm)
        btns.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(btns, text="Zaloguj", command=self.try_login).pack(side="left")
        ttk.Button(btns, text="Anuluj", command=self.destroy).pack(side="right")

        self.entry.focus_set()

    def try_login(self):
        if self.var.get() == notes.PASSWORD:
            self.on_success()
            self.destroy()
        else:
            self.info.config(text="Błędne hasło")
            self.entry.select_range(0,'end')

class MainApp(ttk.Frame):
    def __init__(self,master):
        super().__init__(master, padding=12)
        self.master.title("Notatki")
        self.master.geometry("820x520")
        self.master.minsize(720, 420)
        self.grid(sticky="nsew")

        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        left = ttk.Frame(self)
        left.grid(row=0, column=0, sticky="nsw", padx=(0, 8))
        ttk.Label(left, text="Notatki").pack(anchor="w")

        self.listbox = tk.Listbox(left, height=20)
        self.listbox.pack(fill="y", expand=False)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        lbtns = ttk.Frame(left)
        lbtns.pack(fill="x", pady=(8, 0))
        ttk.Button(lbtns, text="➕ Nowa", command=self.add_note).pack(side="left", padx=(0, 4))
        ttk.Button(lbtns, text="🗑 Usuń", command=self.remove_note).pack(side="left", padx=(0, 4))
        ttk.Button(lbtns, text="⟳ Odśwież", command=self.refresh_list).pack(side="left")

        right = ttk.Frame(self)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        self.title_var = tk.StringVar(value="(brak)")
        ttk.Label(right, textvariable=self.title_var, font=("", 12, "bold")).grid(row=0, column=0, sticky="w")

        self.text = tk.Text(right, wrap="word", undo=True)
        self.text.grid(row=1, column=0, sticky="nsew", pady=(6, 6))

        rbtns = ttk.Frame(right)
        rbtns.grid(row=2, column=0, sticky="ew")
        ttk.Button(rbtns, text="💾 Zapisz (Ctrl+S)", command=self.save_current).pack(side="left")
        ttk.Button(rbtns, text="↪ Cofnij", command=lambda: self.text.edit_undo()).pack(side="left", padx=(6, 0))
        ttk.Button(rbtns, text="↩ Ponów", command=lambda: self.text.edit_redo()).pack(side="left", padx=(6, 0))
        ttk.Button(rbtns, text="Wyszukaj", command=self.search_in_notes).pack(side="right")

        self.master.bind("<Control-s>", lambda e: self.save_current())
        self.current_note = None

        self.disable_ui()
        LoginWindow(self.master, on_success=self.after_login)

    def _set_state_recursive(self,widget,state):
        try:
            widget.configure(state=state)
        except tk.TclError:
            pass
        for ch in getattr(widget,"winfo_children",lambda: [])():
            self._set_state_recursive(ch,state)

    def disable_ui(self):
        for child in self.winfo_children():
            self._set_state_recursive(child,"disabled")
    
    def enable_ui(self):
        for child in self.winfo_children():
            self._set_state_recursive(child,"normal")

    def after_login(self):
        self.enable_ui()
        self.refresh_list()
    
    def refresh_list(self):
        self.listbox.delete(0, "end")
        for n in notes.list_notes():
            self.listbox.insert("end", n)

    def on_select(self, _evt=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        name = self.listbox.get(sel[0])
        self.load_into_editor(name)

    def add_note(self):
            name = simpledialog.askstring("Nowa notatka", "Podaj nazwę (bez spacji / znaków specjalnych):")
            if not name:
                return
            if any(ch in name for ch in "\\/:*?\"<>| "):
                messagebox.showerror("Błąd", "Nazwa zawiera niedozwolone znaki.")
                return
            if notes.os.path.exists(notes.note_path(name)):
                messagebox.showerror("Błąd", "Taka notatka już istnieje.")
                return
            notes.save_note(name, "")
            self.refresh_list()
            self.load_into_editor(name)

    def remove_note(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showinfo("Info", "Wybierz notatkę do usunięcia.")
            return
        name = self.listbox.get(sel[0])
        if messagebox.askyesno("Potwierdź", f"Czy na pewno usunąć „{name}”?"):
            notes.delete_note(name)
            if self.current_note == name:
                self.current_note = None
                self.title_var.set("(brak)")
                self.text.delete("1.0", "end")
            self.refresh_list()

    def load_into_editor(self, name: str):
        try:
            content = notes.load_note(name)
        except FileNotFoundError:
            messagebox.showerror("Błąd", "Nie znaleziono pliku notatki.")
            return
        self.current_note = name
        self.title_var.set(f"Notatka: {name}")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)

    def save_current(self):
        if not self.current_note:
            messagebox.showinfo("Info", "Brak wybranej notatki do zapisania.")
            return
        content = self.text.get("1.0", "end-1c")
        try:
            notes.save_note(self.current_note, content)
            messagebox.showinfo("OK", "Zapisano.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zapisać: {e}")

    def search_in_notes(self):
        query = simpledialog.askstring("Szukaj", "Wpisz szukany tekst:")
        if not query:
            return
        hits = []
        for name in notes.list_notes():
            try:
                txt = notes.load_note(name)
                if query.lower() in txt.lower():
                    hits.append(name)
            except Exception:
                pass
        if hits:
            messagebox.showinfo("Wyniki", "Znaleziono w: " + ", ".join(hits))
        else:
            messagebox.showinfo("Wyniki", "Brak wyników.")