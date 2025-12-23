import sqlite3
import os

# Path to the SQLite file inside the data folder
DB_PATH = os.path.join("data", "Bohra_Calendar_5300AH.sqlite")

def get_connection():
    """
    Creates a new connection to the SQLite database.
    Row factory returns dict-like rows.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
