import os
import base64
from tkinter import ttk
import notes_gui

PASSWORD = "haslo123"
NOTES_DIR = "notes"
EXT = ".txt"

def ensure_dir():
    os.makedirs(NOTES_DIR, exist_ok=True)

def note_path(name: str) -> str:
    return os.path.join(NOTES_DIR, f"note_{name}{EXT}")

def list_notes() -> list[str]:
    ensure_dir()
    notes = []
    for f in os.listdir(NOTES_DIR):
        if f.startswith("note_") and f.endswith(EXT):
            notes.append(f[5:-len(EXT)])
    notes.sort()
    return notes

def save_note(name: str, text: str):
    ensure_dir()
    encoded = base64.b64encode(text.encode()).decode()
    with open(note_path(name), "w", encoding="utf-8") as f:
        f.write(encoded)

def load_note(name: str) -> str:
    with open(note_path(name), "r", encoding="utf-8") as f:
        content = f.read()
    try:
        return base64.b64decode(content.encode()).decode()
    except Exception:
        return ""

def delete_note(name: str):
    p = note_path(name)
    if os.path.exists(p):
        os.remove(p)
    
def main():
    ensure_dir()
    root = notes_gui.tk.Tk()
    try:
        ttk.Style().theme_use("clam")
    except notes_gui.tk.TclError:
        pass
    notes_gui.MainApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()