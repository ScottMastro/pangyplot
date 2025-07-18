import os
import bisect
import sqlite3
import array

NAME = "step_index.db"

def write_step_index(segments, path, chr_dir):
    db_path = os.path.join(chr_dir, NAME)

    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
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

class StepIndex:
    def __init__(self, chr_dir):
        self.db_path = os.path.join(chr_dir, NAME)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()

        # Load start positions for binary search
        self.starts = array.array('I')
        self.ends = array.array('I')
        self._step_to_segment = array.array('I')

        self._load_into_memory()

    def _load_into_memory(self):
        self.cur.execute("SELECT step, seg_id, start, end FROM step_index ORDER BY step")
        for row in self.cur.fetchall():
            self._step_to_segment.append(row["seg_id"])
            self.starts.append(row["start"])
            self.ends.append(row["end"])

    def get_row(self, step):
        self.cur.execute("SELECT * FROM step_index WHERE step = ?", (step,))
        return self.cur.fetchone()

    def __getitem__(self, step):
        row = self.get_row(step)
        if row is None:
            return None
        return row["seg_id"]

    def get_steps_for_segment(self, seg_id):
        self.cur.execute("SELECT step FROM step_index WHERE seg_id = ? ORDER BY step", (seg_id,))
        return [row["step"] for row in self.cur.fetchall()]

    def get_segment_to_steps_dict(self):
        seg_to_steps = {}
        self.cur.execute("SELECT step, seg_id FROM step_index ORDER BY seg_id, step")
        for row in self.cur.fetchall():
            sid = row["seg_id"]
            step = row["step"]
            if sid not in seg_to_steps:
                seg_to_steps[sid] = []
            seg_to_steps[sid].append(step)
        return seg_to_steps

    def get_segment(self, step):
        if step < 0 or step >= len(self.step_to_segment):
            return None
        return self.step_to_segment[step]

    def query_bp(self, bp_position):
        i = bisect.bisect_right(self.starts, bp_position) - 1
        i = max(i, 0)
        return (i, self.starts[i], self.ends[i])

    def query(self, start, end, debug=False):
        res1 = self.query_bp(start)
        res2 = self.query_bp(end)

        if res1 is None or res2 is None:
            raise ValueError("Step not found for the given bp position")

        if debug:
            print(f"""[DEBUG] Position query results {start}-{end}. 
                  START: step={res1[0]} / ref coords {res1[1]}-{res1[2]} / nodes {self.step_to_segment[res1[0]]}
                  END:   step={res2[0]} / ref coords {res2[1]}-{res2[2]} / nodes {self.step_to_segment[res2[0]]}""")
        return (res1[0], res2[0])

    def close(self):
        self.conn.close()