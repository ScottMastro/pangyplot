import os
import sqlite3

NAME="segments.db"

def create_segment_table(db_dir):
    db_path = os.path.join(db_dir, NAME)

    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS segments (
            id INTEGER PRIMARY KEY,
            gc_count INTEGER NOT NULL,
            n_count INTEGER NOT NULL,
            length INTEGER NOT NULL,
            x1 REAL NOT NULL,
            y1 REAL NOT NULL,
            x2 REAL NOT NULL,
            y2 REAL NOT NULL,
            seq TEXT NOT NULL
        );
    """)
    conn.commit()
    return conn

def insert_segment(cur, segment_info):
    cur.execute("""
        INSERT INTO segments (id, gc_count, n_count, length, x1, y1, x2, y2, seq)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        segment_info["id"],
        segment_info["gc_count"],
        segment_info["n_count"],
        segment_info["length"],
        segment_info["x1"],
        segment_info["y1"],
        segment_info["x2"],
        segment_info["y2"],
        segment_info["seq"]
    ))

class SegmentIndex:
    def __init__(self, db_dir):
        db_path = os.path.join(db_dir, NAME)

        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # makes rows accessible as dicts
        self.cur = self.conn.cursor()

    def __getitem__(self, seg_id):
        self.cur.execute("SELECT * FROM segments WHERE id = ?", (seg_id,))
        row = self.cur.fetchone()
        if row is None:
            raise KeyError(f"Segment id {seg_id} not found")
        return dict(row)
    
    def get_by_ids(self, seg_ids):
        placeholders = ','.join(['?'] * len(seg_ids))
        query = f"SELECT * FROM segments WHERE id IN ({placeholders})"
        self.cur.execute(query, seg_ids)
        return [dict(row) for row in self.cur.fetchall()]

    def get_by_range(self, start_id, end_id):
        self.cur.execute("SELECT * FROM segments WHERE id BETWEEN ? AND ?", (start_id, end_id))
        return [dict(row) for row in self.cur.fetchall()]

    def close(self):
        self.conn.close()
