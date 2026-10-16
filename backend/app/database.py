"""
DESHMRITTIKA / BHUMI-SYNC — Database Access Layer
Fast, read-optimized SQLite connection pool with dictionary rows.
"""

import sqlite3
from typing import Generator
from backend.app.config import DATABASE_PATH

def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with dict-like row access."""
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def get_db() -> Generator[sqlite3.Connection, None, None]:
    """FastAPI Dependency yielding database connection."""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()
