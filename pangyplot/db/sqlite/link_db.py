from db.sqlite.common import get_connection
from objects.Link import Link

DB_NAME = "links.db"

def get_connection(chr_dir):
    return get_connection(chr_dir, DB_NAME)

def create_link_table(dir, sample_idx):
    conn = get_connection(dir, DB_NAME, clear_existing=True)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS links (
            id TEXT PRIMARY KEY,
            from_id INTEGER NOT NULL,
            from_strand TEXT NOT NULL,
            to_id INTEGER NOT NULL,
            to_strand TEXT NOT NULL,
            haplotype TEXT NOT NULL,
            reverse TEXT NOT NULL,
            frequency REAL NOT NULL,
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

def insert_link(cur, link):
    key = f"{link.from_id}{link.from_strand}{link.to_id}{link.to_strand}"
    cur.execute("""
        INSERT INTO links (id, from_id, from_strand, to_id, to_strand, haplotype, reverse, frequency)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        key,
        link["from_id"],
        link["from_id"],
        link["from_strand"],
        link["to_id"],
        link["to_strand"],
        link["haplotype"],
        link["reverse"],
        link["frequency"]
    ))

def load_sample_index(self):
    self.cur.execute("SELECT sample, idx FROM sample_index")
    return {row["sample"]: row["idx"] for row in self.cur.fetchall()}

def load_links(cur):
    cur.execute("SELECT from_id, to_id, from_strand, to_strand FROM links")
    return cur.fetchall()

def create_link(row):
    link = Link()
    link.from_id = row["from_id"]
    link.from_strand = row["from_strand"]
    link.to_id = row["to_id"]
    link.to_strand = row["to_strand"]
    link.haplotype = row["haplotype"]
    link.reverse = row["reverse"]
    link.frequency = row["frequency"]
    return link

def get_link(cur, key):
    cur.execute("SELECT * FROM links WHERE id = ?", (key,))
    row = cur.fetchone()
    if row:
        return create_link(row)
    return None