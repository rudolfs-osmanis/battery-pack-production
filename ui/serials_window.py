import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv

from db.order_repo import list_active_orders


class SerialsWindow(tk.Toplevel):
    NOMINAL_CELL_VOLTAGE = 3.7

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.title("Serial Generation & Export")
        self.geometry("980x560")
        self.minsize(920, 500)

        self._orders: dict[str, sqlite3.Row] = {}

        self._build()
        self._bind_events()

        self._load_active_orders()
        self._refresh_order_dropdown()

# ********************* DB connection *********************
    def _conn(self) -> sqlite3.Connection:
        if not hasattr(self.master, "conn"):
            raise RuntimeError("DB connection not found. Ensure app.py sets root.conn = get_connection().")
        return self.master.conn

# ********************* UI Build *********************
    def _build(self) -> None:
        container = ttk.Frame(self, padding=12)
        container.pack(fill="both", expand=True)

        top = ttk.LabelFrame(container, text="Select ACTIVE order and generate serials", padding=12)
        top.pack(fill="x")

        self.order_no_var = tk.StringVar()
        ttk.Label(top, text="Active order:").grid(row=0, column=0, sticky="w")
        self.order_combo = ttk.Combobox(top, textvariable=self.order_no_var, state="readonly", width=22)
        self.order_combo.grid(row=0, column=1, sticky="w", padx=8)

        self.start_no_var = tk.IntVar(value=1)
        ttk.Label(top, text="Start number:").grid(row=0, column=2, sticky="w", padx=(12, 0))
        ttk.Spinbox(top, from_=1, to=1000000, textvariable=self.start_no_var, width=10).grid(
            row=0, column=3, sticky="w", padx=8
        )

        self.pad_width_var = tk.IntVar(value=3)
        ttk.Label(top, text="Pad digits:").grid(row=0, column=4, sticky="w", padx=(12, 0))
        ttk.Spinbox(top, from_=1, to=8, textvariable=self.pad_width_var, width=6).grid(
            row=0, column=5, sticky="w", padx=8
        )

        btns = ttk.Frame(top)
        btns.grid(row=0, column=6, sticky="e", padx=(16, 0))
        ttk.Button(btns, text="Refresh orders", command=self._refresh).pack(fill="x", pady=2)
        ttk.Button(btns, text="Generate", command=self.on_generate).pack(fill="x", pady=2)
        ttk.Button(btns, text="Export CSV", command=self.on_export_csv).pack(fill="x", pady=2)
        ttk.Button(btns, text="Clear table", command=self._clear_table).pack(fill="x", pady=2)

        self.summary_var = tk.StringVar(value="Summary: -")
        ttk.Label(top, textvariable=self.summary_var).grid(row=1, column=0, columnspan=7, sticky="w", pady=(10, 0))

        top.columnconfigure(1, weight=1)

        table_frame = ttk.LabelFrame(container, text="Printer export table", padding=12)
        table_frame.pack(fill="both", expand=True, pady=(12, 0))

        columns = ("serial", "capacity", "voltage")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=16)

        self.tree.heading("serial", text="Serial number")
        self.tree.heading("capacity", text="Capacity(mAh)")
        self.tree.heading("voltage", text="Voltage (V)")

        self.tree.column("serial", width=360, anchor="w")
        self.tree.column("capacity", width=140, anchor="e")
        self.tree.column("voltage", width=140, anchor="e")

        self.tree.pack(fill="both", expand=True)

    def _bind_events(self) -> None:
        self.order_combo.bind("<<ComboboxSelected>>", lambda _e: self._update_summary())


# ********************* Load data *********************
    def _load_active_orders(self) -> None:
        self._orders.clear()
        rows = list_active_orders(self._conn())

        for r in rows:
            self._orders[r["order_no"]] = r

    def _refresh_order_dropdown(self) -> None:
        order_nos = sorted(self._orders.keys())
        self.order_combo["values"] = order_nos
        if order_nos:
            current = self.order_no_var.get().strip()
            if current not in order_nos:
                self.order_no_var.set(order_nos[0])
            self._update_summary()
        else:
            self.order_no_var.set("")
            self.summary_var.set("Summary: No ACTIVE orders found.")

    def _refresh(self) -> None:
        self._load_active_orders()
        self._refresh_order_dropdown()
        self._clear_table()


# ********************* Serial generation *********************
    def on_generate(self) -> None:
        self._clear_table()

        order_no = self.order_no_var.get().strip()
        if not order_no:
            messagebox.showinfo("No order", "Select an ACTIVE order.")
            return

        order = self._orders.get(order_no)
        if not order:
            messagebox.showwarning("Order not found", "Selected order is not available. Click 'Refresh orders'.")
            return

        series = int(order["series"])
        parallel = int(order["parallel"])
        cell_cap = int(order["capacity_mah"])
        qty = int(order["pack_count"])

        if qty <= 0:
            messagebox.showwarning("Invalid quantity", "Pack count must be > 0.")
            return

        pack_capacity = cell_cap * parallel
        voltage = series * self.NOMINAL_CELL_VOLTAGE

        start_no = int(self.start_no_var.get())
        pad = int(self.pad_width_var.get())

        prefix = f"{series}S{parallel}P{pack_capacity}"

        for i in range(qty):
            seq = start_no + i
            serial = f"{prefix}-{order_no}-{seq:0{pad}d}"
            self.tree.insert("", "end", values=(serial, pack_capacity, f"{voltage:.1f}"))

        self._update_summary()


# ********************* CSV Export *********************
    def on_export_csv(self) -> None:
        if not self.tree.get_children():
            messagebox.showinfo("Nothing to export", "Generate serials first.")
            return

        path = filedialog.asksaveasfilename(
            title="Export CSV",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["Serial number", "Capacity(mAh)", "Voltage"])
                for iid in self.tree.get_children():
                    serial, cap, volt = self.tree.item(iid, "values")
                    writer.writerow([serial, cap, volt])
        except OSError as e:
            messagebox.showerror("Export failed", f"Could not write file:\n{e}")
            return

        messagebox.showinfo("Export complete", "CSV exported successfully.")


# ********************* Other fubctions *********************
    def _clear_table(self) -> None:
        for iid in self.tree.get_children():
            self.tree.delete(iid)

    def _update_summary(self) -> None:
        order_no = self.order_no_var.get().strip()
        order = self._orders.get(order_no) if order_no else None
        if not order:
            self.summary_var.set("Summary: -")
            return

        series = int(order["series"])
        parallel = int(order["parallel"])
        cell_cap = int(order["capacity_mah"])
        qty = int(order["pack_count"])

        pack_capacity = cell_cap * parallel
        voltage = series * self.NOMINAL_CELL_VOLTAGE

        cell_label = f'{order["manufacturer"]} {order["model_no"]} ({cell_cap}mAh)'
        self.summary_var.set(
            f"Summary: {series}S{parallel}P{pack_capacity} | Order: {order_no} | Qty: {qty} | Voltage: {voltage:.1f} V | Cell: {cell_label}"
        )