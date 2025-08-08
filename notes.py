import os
import base64
import getpass

PASSWORD = "haslo123"

def get_note_filename(note_name):
    return f"note_{note_name}.txt"

def save_note(note_name):
    note = input("Wpisz treść notatki : ")
    encoded_note = base64.b64encode(note.encode()).decode()
    with open(get_note_filename(note_name),'w') as f:
        f.write(encoded_note)
    print("Notatka zapisana i zakodowana.")

def read_note(note_name):
    password = input("Podaj haslo: ")
    fname = get_note_filename(note_name)
    if not os.path.exists(fname):
        print("Brak takiej notatki!")
        return
    with open(fname,'r') as f:
        content = f.read()
    if password == PASSWORD:
        try:
            note = base64.b64decode(content.encode()).decode()
            print(f"Twoja notatka '{note_name}': {note}")
        except Exception:
            print("Blad przy odczycie notatki")
    else:
        print("YOU ARE NOT MY MASTER")
        print(''.join([chr(ord(c)^42) for c in content]))

def edit_note(note_name):
    password = getpass.getpass("Podaj haslo, by edytować: ")
    fname = get_note_filename(note_name)
    if not os.path.exists(fname):
        print("Brak takiej notatki! Dodaj ją najpierw.")
        return
    if password == PASSWORD:
        old_note = ""
        with open(fname,'r') as f:
            content = f.read()
        try:
            old_note = base64.b64decode(content.encode()).decode()
        except Exception:
            old_note = ""
        print("Obecna notatka: ", old_note)
        save_note(note_name)
    else:
        print("NIEPRAWIDŁOWE HASŁO! NIE MOŻESZ MNIE EDYTOWAĆ!")

def notes_list():
    files = [f for f in os.listdir() if f.startswith("note_") and f.endswith(".txt")]
    note_names = [f[5:-4] for f in files]
    if note_names:
        print("Dostępne notatki : ", ", ".join(note_names))
    else:
        print("Brak notatek.")
    

def main():
    while True:
        print("\n---MENU---")
        print("1. Dodaj nową notatkę")
        print("2. Odczytaj notatkę")
        print("3. Edytuj notatkę")
        print("4. Pokaż listę notatek")
        print("5. Zakończ")
        choice = input("Wybierz opcję : ")
        match int(choice):
            case 1:
                note_name = input("Podaj nazwę notatki : ")
                save_note(note_name)
            case 2:
                note_name = input("Podaj nazwę notatki do odczytu: ")
                read_note(note_name)
            case 3:
                note_name  = input("Podaj nazwę notatki do edycji : ")
                edit_note(note_name)
            case 4:
                notes_list()
            case 5:
                print("Do następnego")
                break

if __name__ == "__main__":
    main()

