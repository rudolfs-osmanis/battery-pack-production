import tkinter as tk
from tkinter import ttk, messagebox
from db.cell_repo import list_cells, insert_cell, update_cell, delete_cell


class CellsWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master)
        self.title("Cell Parameters")
        self.geometry("860x480")
        self.minsize(820, 420)

        self._build()
        self._bind_events()

    def _build(self) -> None:
        container = ttk.Frame(self, padding=12)
        container.pack(fill="both", expand=True)

# ********************* Form *********************
        form = ttk.LabelFrame(container, text="Add / Edit cell", padding=12)
        form.pack(fill="x")

        self.manufacturer_var = tk.StringVar()
        self.model_no_var = tk.StringVar()
        self.capacity_var = tk.IntVar(value=0)
        self.unit_price_var = tk.DoubleVar(value=0.0)

        ttk.Label(form, text="Manufacturer:").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.manufacturer_var, width=28).grid(row=0, column=1, sticky="w", padx=8)

        ttk.Label(form, text="Cell model no:").grid(row=0, column=2, sticky="w", padx=(12, 0))
        ttk.Entry(form, textvariable=self.model_no_var, width=28).grid(row=0, column=3, sticky="w", padx=8)

        ttk.Label(form, text="Capacity (mAh):").grid(row=1, column=0, sticky="w", pady=(10, 0))
        ttk.Spinbox(form, from_=0, to=200000, textvariable=self.capacity_var, width=12).grid(
            row=1, column=1, sticky="w", padx=8, pady=(10, 0)
        )

        ttk.Label(form, text="Unit price:").grid(row=1, column=2, sticky="w", padx=(12, 0), pady=(10, 0))
        ttk.Entry(form, textvariable=self.unit_price_var, width=14).grid(
            row=1, column=3, sticky="w", padx=8, pady=(10, 0)
        )

# ********************* Buttons *********************
        btns = ttk.Frame(form)
        btns.grid(row=0, column=4, rowspan=2, sticky="e", padx=(16, 0))

        ttk.Button(btns, text="Add new", command=self.on_add).pack(fill="x", pady=2)
        ttk.Button(btns, text="Save changes", command=self.on_save).pack(fill="x", pady=2)
        ttk.Button(btns, text="Delete", command=self.on_delete).pack(fill="x", pady=2)
        ttk.Button(btns, text="Clear", command=self._clear_form).pack(fill="x", pady=2)

        # Status line
        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(form, textvariable=self.status_var).grid(row=2, column=0, columnspan=5, sticky="w", pady=(10, 0))

        # Let's the model field row expand if needed
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

# ********************* List *********************
        list_frame = ttk.LabelFrame(container, text="Existing cells", padding=12)
        list_frame.pack(fill="both", expand=True, pady=(12, 0))

        columns = ("manufacturer", "model_no", "capacity", "unit_price")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)

        self.tree.heading("manufacturer", text="Manufacturer")
        self.tree.heading("model_no", text="Cell model no")
        self.tree.heading("capacity", text="Capacity (mAh)")
        self.tree.heading("unit_price", text="Unit price")

        self.tree.column("manufacturer", width=180, anchor="w")
        self.tree.column("model_no", width=180, anchor="w")
        self.tree.column("capacity", width=120, anchor="e")
        self.tree.column("unit_price", width=120, anchor="e")

        self.tree.pack(fill="both", expand=True)

        self._load_cells()

    def _bind_events(self) -> None:
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)


# ********************* UI functions *********************
    def on_add(self) -> None:
        data = self._read_form_validated()
        if data is None:
            return
        manufacturer, model_no, capacity, unit_price = data
        try:
            new_id = insert_cell(self._conn(), manufacturer, model_no, capacity, unit_price)
        except Exception as e:
            messagebox.showerror("DB error", str(e))
            return
        self.status_var.set("Added.")
        self._load_cells()
        self.tree.selection_set(str(new_id))

    def on_save(self) -> None:
        selected = self._selected_iid()
        if selected is None:
            messagebox.showinfo("No selection", "Select an existing cell row to edit, or use 'Add new'.")
            return

        data = self._read_form_validated()
        if data is None:
            return
        manufacturer, model_no, capacity, unit_price = data

        try:
            update_cell(self._conn(), int(selected), manufacturer, model_no, capacity, unit_price)
        except Exception as e:
            messagebox.showerror("DB error", str(e))
            return

        self.status_var.set("Saved.")
        self._load_cells()
        self.tree.selection_set(selected)

    def on_delete(self) -> None:
        selected = self._selected_iid()
        if selected is None:
            messagebox.showinfo("No selection", "Select a row to delete.")
            return

        vals = self.tree.item(selected, "values")
        if not messagebox.askyesno("Confirm delete", f"Delete this cell?\n\n{vals[0]} / {vals[1]}"):
            return

        try:
            delete_cell(self._conn(), int(selected))
        except Exception as e:
            messagebox.showerror("DB error", str(e))
            return

        self.status_var.set("Deleted.")
        self._clear_form()
        self._load_cells()


# ********************* General functions *********************
    def _conn(self):
        return self.master.conn
    
    def _on_tree_select(self, _event: object) -> None:
        selected = self._selected_iid()
        if selected is None:
            return
        manufacturer, model_no, capacity, unit_price = self.tree.item(selected, "values")

        self.manufacturer_var.set(manufacturer)
        self.model_no_var.set(model_no)
        self.capacity_var.set(int(capacity))

        try:
            self.unit_price_var.set(float(unit_price))
        except ValueError:
            self.unit_price_var.set(0.0)

        self.status_var.set(f"Editing: {manufacturer} / {model_no}")

    def _selected_iid(self) -> str | None:
        sel = self.tree.selection()
        return sel[0] if sel else None

    def _clear_form(self) -> None:
        self.manufacturer_var.set("")
        self.model_no_var.set("")
        self.capacity_var.set(0)
        self.unit_price_var.set(0.0)
        self.status_var.set("Ready.")
        self.tree.selection_remove(self.tree.selection())

    def _read_form_validated(self) -> tuple[str, str, int, float] | None:
        manufacturer = self.manufacturer_var.get().strip()
        model_no = self.model_no_var.get().strip()

        if not manufacturer:
            messagebox.showwarning("Validation", "Manufacturer is required.")
            return None
        if not model_no:
            messagebox.showwarning("Validation", "Cell model no is required.")
            return None

        try:
            capacity = int(self.capacity_var.get())
        except Exception:
            messagebox.showwarning("Validation", "Capacity must be an integer.")
            return None
        if capacity <= 0:
            messagebox.showwarning("Validation", "Capacity must be > 0.")
            return None

        try:
            unit_price = float(self.unit_price_var.get())
        except Exception:
            messagebox.showwarning("Validation", "Unit price must be a number.")
            return None
        if unit_price < 0:
            messagebox.showwarning("Validation", "Unit price cannot be negative.")
            return None

        return manufacturer, model_no, capacity, unit_price

    def _load_cells(self) -> None:
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        for row in list_cells(self._conn()):
            self.tree.insert(
                "",
                "end",
                iid=str(row["id"]),
                values=(row["manufacturer"], row["model_no"], row["capacity_mah"], f'{row["unit_price_eur"]:.2f}')
            )