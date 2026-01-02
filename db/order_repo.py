import sqlite3

def get_last_order_no(conn: sqlite3.Connection) -> str | None:
    row = conn.execute("SELECT order_no FROM orders ORDER BY id DESC LIMIT 1").fetchone()
    return row["order_no"] if row else None

def insert_order(conn: sqlite3.Connection, order_no: str, client: str, pack_count: int, notes: str,
                 series: int, parallel: int, cell_id: int, status: str) -> int:
    cur = conn.execute("""
        INSERT INTO orders (order_no, client, pack_count, notes, series, parallel, cell_id, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (order_no, client, pack_count, notes, series, parallel, cell_id, status))
    conn.commit()
    return int(cur.lastrowid)

def update_order(conn: sqlite3.Connection, order_id: int, client: str, pack_count: int, notes: str,
                 series: int, parallel: int, cell_id: int, status: str) -> None:
    conn.execute("""
        UPDATE orders
        SET client=?, pack_count=?, notes=?, series=?, parallel=?, cell_id=?, status=?
        WHERE id=?
    """, (client, pack_count, notes, series, parallel, cell_id, status, order_id))
    conn.commit()

def list_orders(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(conn.execute("""
        SELECT o.id, o.order_no, o.client, o.pack_count, o.notes, o.series, o.parallel, o.status,
               c.manufacturer, c.model_no, c.capacity_mah, c.unit_price_eur, o.cell_id
        FROM orders o
        JOIN cells c ON c.id = o.cell_id
        ORDER BY o.id DESC
    """))

def list_active_orders(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return list(conn.execute("""
        SELECT o.id, o.order_no, o.pack_count, o.series, o.parallel, o.notes,
               c.capacity_mah, c.unit_price_eur, c.manufacturer, c.model_no, o.cell_id
        FROM orders o
        JOIN cells c ON c.id = o.cell_id
        WHERE o.status='ACTIVE'
        ORDER BY o.id DESC
    """))