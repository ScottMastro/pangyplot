import os
import sqlite3
from array import array

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
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

        self.cur.execute("SELECT MAX(id) FROM segments")
        self.max_id = self.cur.fetchone()[0]

        self.gc_count = array('I', [0] * (self.max_id + 1))
        self.n_count  = array('I', [0] * (self.max_id + 1))
        self.length   = array('I', [0] * (self.max_id + 1))
        self.x1       = array('f', [0.0] * (self.max_id + 1))
        self.y1       = array('f', [0.0] * (self.max_id + 1))
        self.x2       = array('f', [0.0] * (self.max_id + 1))
        self.y2       = array('f', [0.0] * (self.max_id + 1))

        self._load_metadata_into_arrays()

    def _load_metadata_into_arrays(self):
        self.cur.execute("SELECT id, gc_count, n_count, length, x1, y1, x2, y2 FROM segments")
        for row in self.cur.fetchall():
            sid = row["id"]
            self.gc_count[sid] = row["gc_count"]
            self.n_count[sid]  = row["n_count"]
            self.length[sid]   = row["length"]
            self.x1[sid]       = row["x1"]
            self.y1[sid]       = row["y1"]
            self.x2[sid]       = row["x2"]
            self.y2[sid]       = row["y2"]

    def __getitem__(self, seg_id):
        if seg_id < 0 or seg_id >= self.max_id:
            return None
        return {
            "id": seg_id,
            "gc_count": self.gc_count[seg_id],
            "n_count": self.n_count[seg_id],
            "length": self.length[seg_id],
            "x1": self.x1[seg_id],
            "y1": self.y1[seg_id],
            "x2": self.x2[seg_id],
            "y2": self.y2[seg_id]
        }

    def get_by_ids(self, seg_ids, with_seq=False):
        results = []
        for sid in seg_ids:
            seg = self[sid]
            if seg is None:
                continue
            results.append(seg)

        if not with_seq:
            return results

        for seg in results:
            self.cur.execute("SELECT seq FROM segments WHERE id = ?", (seg["id"],))
            row = self.cur.fetchone()
            seg["seq"] = row["seq"] if row else None

        return results

    def get_between(self, start_id, end_id, with_seq=False):
        results = []
        for sid in range(start_id, end_id + 1):
            if sid < 0 or sid >= self.max_id:
                continue
            seg = self[sid]
            if seg is not None:
                results.append(seg)

        if with_seq:
            for seg in results:
                self.cur.execute("SELECT seq FROM segments WHERE id = ?", (seg["id"],))
                row = self.cur.fetchone()
                seg["seq"] = row["seq"] if row else None

        return results

    def close(self):
        self.conn.close()
