import os
import sqlite3

NAME = "step_index.db"

def get_connection(chr_dir, clear_existing=False):
    db_path = os.path.join(chr_dir, NAME)

    if clear_existing and os.path.exists(db_path):
            os.remove(db_path)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def write_step_index(segments, path, chr_dir):
    conn = get_connection(chr_dir, clear_existing=True)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE step_index (
            step INTEGER PRIMARY KEY,
            seg_id INTEGER NOT NULL,
            start INTEGER NOT NULL,
            end INTEGER NOT NULL
        );
    """)
    cur.execute("CREATE INDEX idx_seg_id ON step_index(seg_id);")

    pos = 1
    for i, step in enumerate(path["path"]):
        sid = int(step[:-1])
        length = segments[sid]["length"]
        start = pos
        end = pos + length - 1
        cur.execute("INSERT INTO step_index (step, seg_id, start, end) VALUES (?, ?, ?, ?)",
                    (i, sid, start, end))
        pos += length

    conn.commit()
    conn.close()
