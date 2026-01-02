import tkinter as tk

from ui.main_window import MainWindow
from db.connection import get_connection
from db.schema import ensure_schema

def main() -> None:
    conn = get_connection()
    ensure_schema(conn)

    root = tk.Tk()
    root.title("Battery Production System")
    root.geometry("420x260")
    root.minsize(420, 260)

    root.conn = conn

    MainWindow(root)

    def on_close() -> None:
        try:
            conn.close()
        finally:
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

if __name__ == "__main__":
    main()