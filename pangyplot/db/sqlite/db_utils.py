import os
import sqlite3

def get_connection(dir, filename, clear_existing=False):
    db_path = os.path.join(dir, filename)

    if clear_existing and os.path.exists(db_path):
            os.remove(db_path)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
