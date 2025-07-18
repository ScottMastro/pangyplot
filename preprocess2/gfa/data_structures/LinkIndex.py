import os
import sqlite3

NAME = "links.db"

def create_link_table(db_dir, sample_idx):
    db_path = os.path.join(db_dir, NAME)

    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS links (
            from_id INTEGER NOT NULL,
            from_strand TEXT NOT NULL,
            to_id INTEGER NOT NULL,
            to_strand TEXT NOT NULL,
            haplotype TEXT NOT NULL,
            reverse TEXT NOT NULL,
            frequency REAL NOT NULL,
            PRIMARY KEY (from_id, to_id)
        );
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_from_id ON links(from_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_to_id ON links(to_id);")

    cur.execute("CREATE TABLE IF NOT EXISTS sample_index ("
                "sample TEXT PRIMARY KEY,"
                "idx INTEGER NOT NULL"
                ");")
    
    cur.executemany("""
        INSERT INTO sample_index (sample, idx)
        VALUES (?, ?)
    """, sample_idx.items())

    conn.commit()
    return conn

def read_sample_index(cur):
    cur.execute("SELECT sample, idx FROM sample_index")
    return {row["sample"]: row["idx"] for row in cur.fetchall()}

def insert_link(cur, link):
    cur.execute("""
        INSERT INTO links (from_id, from_strand, to_id, to_strand, haplotype, reverse, frequency)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        link["from_id"],
        link["from_strand"],
        link["to_id"],
        link["to_strand"],
        link["haplotype"],
        link["reverse"],
        link["frequency"]
    ))

class LinkIndex:
    def __init__(self, db_dir):
        db_path = os.path.join(db_dir, NAME)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        self.sample_idx = read_sample_index(self.cur)

    def __getitem__(self, key):
        if isinstance(key, tuple) and len(key) == 2:
            # Case 1: (from_id, to_id)
            from_id, to_id = key
            self.cur.execute("""
                SELECT * FROM links WHERE from_id = ? AND to_id = ?
            """, (from_id, to_id))
            row = self.cur.fetchone()
            if row is None:
                raise KeyError(f"Link ({from_id}, {to_id}) not found")
            return dict(row)

        elif isinstance(key, int):
            # Case 2: single node_id
            node_id = key
            self.cur.execute("SELECT * FROM links WHERE from_id = ?", (node_id,))
            from_links = [dict(row) for row in self.cur.fetchall()]

            self.cur.execute("SELECT * FROM links WHERE to_id = ?", (node_id,))
            to_links = [dict(row) for row in self.cur.fetchall()]

            return from_links, to_links
        else:
            raise TypeError("Key must be an int (node_id) or a tuple of two ints (from_id, to_id)")

    def get_by_from_id(self, from_id):
        self.cur.execute("SELECT * FROM links WHERE from_id = ?", (from_id,))
        return [dict(row) for row in self.cur.fetchall()]

    def get_by_range(self, start_id, end_id):
        self.cur.execute("""
            SELECT * FROM links
            WHERE from_id BETWEEN ? AND ?
        """, (start_id, end_id))
        return [dict(row) for row in self.cur.fetchall()]

    def close(self):
        self.conn.close()
