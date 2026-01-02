import sqlite3
from typing import Iterable

def list_cells(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(conn.execute("""
        SELECT id, manufacturer, model_no, capacity_mah, unit_price_eur
        FROM cells
        ORDER BY manufacturer, model_no
    """))

def insert_cell(conn: sqlite3.Connection, manufacturer: str, model_no: str, capacity_mah: int, unit_price_eur: float) -> int:
    cur = conn.execute("""
        INSERT INTO cells (manufacturer, model_no, capacity_mah, unit_price_eur)
        VALUES (?, ?, ?, ?)
    """, (manufacturer, model_no, capacity_mah, unit_price_eur))
    conn.commit()
    return int(cur.lastrowid)

def update_cell(conn: sqlite3.Connection, cell_id: int, manufacturer: str, model_no: str, capacity_mah: int, unit_price_eur: float) -> None:
    conn.execute("""
        UPDATE cells
        SET manufacturer=?, model_no=?, capacity_mah=?, unit_price_eur=?
        WHERE id=?
    """, (manufacturer, model_no, capacity_mah, unit_price_eur, cell_id))
    conn.commit()

def delete_cell(conn: sqlite3.Connection, cell_id: int) -> None:
    conn.execute("DELETE FROM cells WHERE id=?", (cell_id,))
    conn.commit()