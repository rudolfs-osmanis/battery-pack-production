import sqlite3

def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cells (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manufacturer TEXT NOT NULL,
            model_no TEXT NOT NULL,
            capacity_mah INTEGER NOT NULL,
            unit_price_eur REAL NOT NULL,
            UNIQUE(manufacturer, model_no)
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_no TEXT NOT NULL UNIQUE,
            client TEXT NOT NULL,
            pack_count INTEGER NOT NULL,
            notes TEXT NOT NULL DEFAULT '',
            series INTEGER NOT NULL,
            parallel INTEGER NOT NULL,
            cell_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'ACTIVE',
            FOREIGN KEY(cell_id) REFERENCES cells(id)
        );
    """)

    conn.commit()