import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

from db.cell_repo import list_cells
from db.order_repo import (
    get_last_order_no,
    insert_order,
    update_order,
    list_orders,
)


class OrdersWindow(tk.Toplevel):
    STATUSES = ("ACTIVE", "DISCONTINUED", "FINISHED")

    NOMINAL_CELL_VOLTAGE = 3.7

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.title("Orders")
        self.geometry("980x560")
        self.minsize(920, 500)

        self._cell_map: dict[str, sqlite3.Row] = {}

        self._selected_iid: str | None = None

        self._build()
        self._bind_events()

        self._load_cells_into_combo()
        self._load_orders()
        self._set_next_order_number()

# ********************* DB connection *********************
    def _conn(self) -> sqlite3.Connection:
        if not hasattr(self.master, "conn"):
            raise RuntimeError("DB connection not found. Ensure app.py sets root.conn = get_connection().")
        return self.master.conn  # type: ignore[attr-defined]

# ********************* UI *********************
    def _build(self) -> None:
        container = ttk.Frame(self, padding=12)
        container.pack(fill="both", expand=True)

        form = ttk.LabelFrame(container, text="Register / Edit order", padding=12)
        form.pack(fill="x")

        self.order_no_var = tk.StringVar()
        self.client_var = tk.StringVar()
        self.pack_count_var = tk.IntVar(value=1)
        self.status_var = tk.StringVar(value="ACTIVE")

        ttk.Label(form, text="Order No:").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.order_no_var, width=18, state="readonly").grid(
            row=0, column=1, sticky="w", padx=8
        )

        ttk.Label(form, text="Client:").grid(row=0, column=2, sticky="w", padx=(12, 0))
        ttk.Entry(form, textvariable=self.client_var, width=28).grid(row=0, column=3, sticky="w", padx=8)

        ttk.Label(form, text="Pack count:").grid(row=0, column=4, sticky="w", padx=(12, 0))
        ttk.Spinbox(form, from_=1, to=1000000, textvariable=self.pack_count_var, width=10).grid(
            row=0, column=5, sticky="w", padx=8
        )

        ttk.Label(form, text="Status:").grid(row=0, column=6, sticky="w", padx=(12, 0))
        ttk.Combobox(form, textvariable=self.status_var, values=self.STATUSES, state="readonly", width=14).grid(
            row=0, column=7, sticky="w", padx=8
        )

# ********************* Buttons *********************
        btns = ttk.Frame(form)
        btns.grid(row=0, column=8, rowspan=3, sticky="ne", padx=(16, 0))

        ttk.Button(btns, text="New order", command=self._new_order).pack(fill="x", pady=2)
        ttk.Button(btns, text="Save", command=self.on_save).pack(fill="x", pady=2)
        ttk.Button(btns, text="Update", command=self.on_update).pack(fill="x", pady=2)
        ttk.Button(btns, text="Clear", command=self._clear_form).pack(fill="x", pady=2)

        self.config_var = tk.StringVar()
        ttk.Label(form, text="Config / notes:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(form, textvariable=self.config_var).grid(
            row=1, column=1, columnspan=7, sticky="we", padx=8, pady=(10, 0)
        )

        self.parallel_var = tk.StringVar(value="1P")
        self.series_var = tk.StringVar(value="1S")
        self.cell_label_var = tk.StringVar()

        parallel_values = [f"{p}P" for p in range(1, 21)]
        series_values = [f"{s}S" for s in range(1, 21)]

        ttk.Label(form, text="Parallel:").grid(row=2, column=0, sticky="w", pady=(10, 0))
        ttk.Combobox(form, textvariable=self.parallel_var, values=parallel_values, state="readonly", width=8).grid(
            row=2, column=1, sticky="w", padx=8, pady=(10, 0)
        )

        ttk.Label(form, text="Series:").grid(row=2, column=2, sticky="w", padx=(12, 0), pady=(10, 0))
        ttk.Combobox(form, textvariable=self.series_var, values=series_values, state="readonly", width=8).grid(
            row=2, column=3, sticky="w", padx=8, pady=(10, 0)
        )

        ttk.Label(form, text="Cell model:").grid(row=2, column=4, sticky="w", padx=(12, 0), pady=(10, 0))
        self.cell_combo = ttk.Combobox(
            form,
            textvariable=self.cell_label_var,
            values=[],
            state="readonly",
            width=34,
        )
        self.cell_combo.grid(row=2, column=5, columnspan=3, sticky="w", padx=8, pady=(10, 0))

# ********************* Summary *********************
        self.summary_var = tk.StringVar(value="Summary: -")
        ttk.Label(form, textvariable=self.summary_var).grid(row=3, column=0, columnspan=9, sticky="w", pady=(12, 0))

        self.info_var = tk.StringVar(value="Ready.")
        ttk.Label(form, textvariable=self.info_var).grid(row=4, column=0, columnspan=9, sticky="w", pady=(6, 0))

        form.columnconfigure(3, weight=1)
        form.columnconfigure(5, weight=1)

# ********************* List *********************
        list_frame = ttk.LabelFrame(container, text="Existing orders", padding=12)
        list_frame.pack(fill="both", expand=True, pady=(12, 0))

        columns = ("order_no", "client", "pack_count", "layout", "cell", "status", "notes")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=14)

        for col, text in [
            ("order_no", "Order No"),
            ("client", "Client"),
            ("pack_count", "Count"),
            ("layout", "Layout"),
            ("cell", "Cell"),
            ("status", "Status"),
            ("notes", "Notes"),
        ]:
            self.tree.heading(col, text=text)

        self.tree.column("order_no", width=110, anchor="w")
        self.tree.column("client", width=160, anchor="w")
        self.tree.column("pack_count", width=70, anchor="e")
        self.tree.column("layout", width=80, anchor="w")
        self.tree.column("cell", width=240, anchor="w")
        self.tree.column("status", width=120, anchor="w")
        self.tree.column("notes", width=260, anchor="w")

        self.tree.pack(fill="both", expand=True)

    def _bind_events(self) -> None:
        for var in (self.parallel_var, self.series_var, self.cell_label_var, self.config_var, self.pack_count_var):
            var.trace_add("write", lambda *_: self._update_summary())

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.cell_combo.bind("<<ComboboxSelected>>", lambda _e: self._update_summary())


# ********************* Loaders *********************
    def _load_cells_into_combo(self) -> None:
        self._cell_map.clear()
        labels: list[str] = []

        rows = list_cells(self._conn())
        for r in rows:
            # Stable human-readable label
            label = f'{r["manufacturer"]} {r["model_no"]} ({r["capacity_mah"]}mAh, €{r["unit_price_eur"]:.2f})'
            self._cell_map[label] = r
            labels.append(label)

        self.cell_combo["values"] = labels
        if labels and not self.cell_label_var.get():
            self.cell_label_var.set(labels[0])

    def _load_orders(self) -> None:
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        for r in list_orders(self._conn()):
            layout = f'{r["series"]}S{r["parallel"]}P'
            cell_label = f'{r["manufacturer"]} {r["model_no"]} ({r["capacity_mah"]}mAh)'
            self.tree.insert(
                "",
                "end",
                iid=str(r["id"]),
                values=(r["order_no"], r["client"], r["pack_count"], layout, cell_label, r["status"], r["notes"]),
            )

# ********************* Order nr. generation *********************
    def _set_next_order_number(self) -> None:
        last = get_last_order_no(self._conn())
        self.order_no_var.set(self._next_order_no(last))

    def _next_order_no(self, last: str | None) -> str:
        if not last:
            return "ORD-0001"

        s = last.strip().upper()

        digits = ""
        for ch in reversed(s):
            if ch.isdigit():
                digits = ch + digits
            else:
                break
        if not digits:
            return "ORD-0001"

        n = int(digits) + 1
        return f"ORD-{n:04d}"


# ********************* UI functions *********************
    def _new_order(self) -> None:
        self._clear_form()
        self._set_next_order_number()
        self.info_var.set("New order ready.")

    def on_save(self) -> None:
        payload = self._read_form_validated()
        if payload is None:
            return

        order_no, client, pack_count, notes, series_count, parallel_count, cell_id, status = payload

        try:
            insert_order(self._conn(), order_no, client, pack_count, notes, series_count, parallel_count, cell_id, status)
        except sqlite3.IntegrityError as e:
            messagebox.showerror("DB error", f"Could not save order.\n\n{e}")
            return
        except Exception as e:
            messagebox.showerror("DB error", str(e))
            return

        self.info_var.set("Order saved.")
        self._load_orders()
        self._new_order()

    def on_update(self) -> None:
        if self._selected_iid is None:
            messagebox.showinfo("No selection", "Select an existing order row to update.")
            return

        payload = self._read_form_validated()
        if payload is None:
            return

        order_no, client, pack_count, notes, series_count, parallel_count, cell_id, status = payload

        try:
            update_order(self._conn(), int(self._selected_iid), client, pack_count, notes, series_count, parallel_count, cell_id, status)
        except Exception as e:
            messagebox.showerror("DB error", str(e))
            return

        self.info_var.set("Order updated.")
        self._load_orders()
        self.tree.selection_set(self._selected_iid)
        self.tree.focus(self._selected_iid)
        self.tree.see(self._selected_iid)


# ********************* Selection and checks *********************
    def _on_tree_select(self, _event: object) -> None:
        sel = self.tree.selection()
        if not sel:
            return
        self._selected_iid = sel[0]

        order_no, client, pack_count, layout, cell_label, status, notes = self.tree.item(self._selected_iid, "values")

        self.order_no_var.set(order_no)
        self.client_var.set(client)
        self.pack_count_var.set(int(pack_count))
        self.status_var.set(status)
        self.config_var.set(notes)

        # parse layout "4S2P"
        try:
            s_idx = layout.index("S")
            p_idx = layout.index("P")
            self.series_var.set(layout[: s_idx + 1])
            self.parallel_var.set(layout[s_idx + 1 : p_idx + 1])
        except Exception:
            pass

        current_values = list(self.cell_combo["values"])
        for lbl in current_values:
            if cell_label.split("(")[0].strip() in lbl:
                self.cell_label_var.set(lbl)
                break

        self._update_summary()
        self.info_var.set(f"Editing: {order_no}")

    def _read_form_validated(self) -> tuple[str, str, int, str, int, int, int, str] | None:
        order_no = self.order_no_var.get().strip()
        client = self.client_var.get().strip()
        notes = self.config_var.get().strip()

        if not order_no:
            messagebox.showwarning("Validation", "Order number is missing.")
            return None
        if not client:
            messagebox.showwarning("Validation", "Client is required.")
            return None

        try:
            pack_count = int(self.pack_count_var.get())
        except Exception:
            messagebox.showwarning("Validation", "Pack count must be an integer.")
            return None
        if pack_count <= 0:
            messagebox.showwarning("Validation", "Pack count must be > 0.")
            return None

        series = self.series_var.get().strip()
        parallel = self.parallel_var.get().strip()
        if not series.endswith("S") or not parallel.endswith("P"):
            messagebox.showwarning("Validation", "Series/Parallel selection is invalid.")
            return None

        try:
            series_count = int(series[:-1])
            parallel_count = int(parallel[:-1])
        except Exception:
            messagebox.showwarning("Validation", "Series/Parallel values are invalid.")
            return None

        cell_label = self.cell_label_var.get().strip()
        if not cell_label or cell_label not in self._cell_map:
            messagebox.showwarning("Validation", "Please select a cell model.")
            return None
        cell_id = int(self._cell_map[cell_label]["id"])

        status = self.status_var.get().strip()
        if status not in self.STATUSES:
            messagebox.showwarning("Validation", "Invalid status.")
            return None

        return (order_no, client, pack_count, notes, series_count, parallel_count, cell_id, status)

    def _clear_form(self) -> None:
        self.client_var.set("")
        self.pack_count_var.set(1)
        self.config_var.set("")
        self.parallel_var.set("1P")
        self.series_var.set("1S")
        self.status_var.set("ACTIVE")
        self._selected_iid = None
        self.tree.selection_remove(self.tree.selection())

        if self.cell_combo["values"] and not self.cell_label_var.get():
            self.cell_label_var.set(self.cell_combo["values"][0])

        self._update_summary()


# ********************* Summary generation *********************
    def _update_summary(self) -> None:
        series = self.series_var.get().strip()
        parallel = self.parallel_var.get().strip()

        try:
            s_count = int(series[:-1]) if series.endswith("S") else 0
            p_count = int(parallel[:-1]) if parallel.endswith("P") else 0
        except Exception:
            s_count = p_count = 0

        pack_qty = int(self.pack_count_var.get() or 0)

        cell_label = self.cell_label_var.get().strip()
        cell_row = self._cell_map.get(cell_label)

        if cell_row and s_count and p_count:
            cap_cell = int(cell_row["capacity_mah"])
            price = float(cell_row["unit_price_eur"])

            pack_capacity = cap_cell * p_count
            total_cost = price * s_count * p_count * pack_qty
            voltage = s_count * self.NOMINAL_CELL_VOLTAGE

            notes = self.config_var.get().strip()
            extra = f" {notes}" if notes else ""

            self.summary_var.set(
                f"Summary: {s_count}S{p_count}P {pack_capacity} mAh | Voltage: {voltage:.1f} V | Cell cost: €{total_cost:.2f}{extra}"
            )
        else:
            self.summary_var.set("Summary: -")