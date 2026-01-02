import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).resolve().parent.parent / "battery_system.sqlite3"

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn