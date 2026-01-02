import tkinter as tk
from tkinter import ttk

from ui.cells_window import CellsWindow
from ui.orders_window import OrdersWindow
from ui.serials_window import SerialsWindow


class MainWindow(ttk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=16)
        self.master = master
        self.pack(fill="both", expand=True)

        self._cells_win: CellsWindow | None = None
        self._orders_win: OrdersWindow | None = None
        self._serials_win: SerialsWindow | None = None

        self._build()

    def _build(self) -> None:
        title = ttk.Label(self, text="Main Menu", font=("Segoe UI", 14, "bold"))
        title.pack(anchor="w")

        ttk.Label(self, text="Choose a module:").pack(anchor="w", pady=(8, 12))

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x")

        ttk.Button(
            btn_frame,
            text="Cell parameter registration",
            command=self.open_cells,
        ).pack(fill="x", pady=4)

        ttk.Button(
            btn_frame,
            text="Order registration",
            command=self.open_orders,
        ).pack(fill="x", pady=4)

        ttk.Button(
            btn_frame,
            text="Serial generation & export",
            command=self.open_serials,
        ).pack(fill="x", pady=4)

        ttk.Separator(self).pack(fill="x", pady=12)

        ttk.Label(
            self,
            text="version 0.9 (beta)",
        ).pack(anchor="w")

    def _bring_to_front(self, win: tk.Toplevel) -> None:
        win.deiconify()
        win.lift()
        win.focus_force()

    def open_cells(self) -> None:
        if self._cells_win is None or not self._cells_win.winfo_exists():
            self._cells_win = CellsWindow(self.master)
        self._bring_to_front(self._cells_win)

    def open_orders(self) -> None:
        if self._orders_win is None or not self._orders_win.winfo_exists():
            self._orders_win = OrdersWindow(self.master)
        self._bring_to_front(self._orders_win)

    def open_serials(self) -> None:
        if self._serials_win is None or not self._serials_win.winfo_exists():
            self._serials_win = SerialsWindow(self.master)
        self._bring_to_front(self._serials_win)