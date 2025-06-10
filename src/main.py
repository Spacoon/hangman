from tkinter import Tk
from database import init_db
from gui import HangmanApp

if __name__ == "__main__":
    init_db()
    root = Tk()
    app = HangmanApp(root)
    root.mainloop()