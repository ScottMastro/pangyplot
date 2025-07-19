import os
import sqlite3
from array import array
from collections import defaultdict
from bitarray import bitarray
import time

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
            PRIMARY KEY (from_id, from_strand, to_id, to_strand)

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

        self.sample_idx = self._read_sample_index()
        
        self.from_ids = array('I')
        self.to_ids = array('I')
        self.from_strands = bitarray()
        self.to_strands = bitarray()

        self.seg_index_offsets = array('I')   # start index into self.seg_index_flat
        self.seg_index_counts  = array('B')   # max 255 links per segment
        self.seg_index_flat    = array('I')   # flattened list of link indices

        self.strand_map = {'+': 1, '-': 0}
        self.rev_strand_map = {1: '+', 0: '-'}
        self._load_links()

    def _read_sample_index(self):
        self.cur.execute("SELECT sample, idx FROM sample_index")
        return {row["sample"]: row["idx"] for row in self.cur.fetchall()}
        
    def __getitem__(self, key):

        if isinstance(key, tuple) and len(key) == 2:
            from_id, to_id = key
            for i in self.from_index.get(from_id, []):
                if self.to_ids[i] == to_id:
                    return self.get_link_by_index(i)
            raise KeyError(f"Link ({from_id}, {to_id}) not found")

        elif isinstance(key, int):
            return self.get_links_by_segment(key)

        else:
            raise TypeError("Key must be int or tuple of two ints")

    def _load_links(self):
        time_start = time.time()

        self.cur.execute("SELECT * FROM links")
        rows = self.cur.fetchall()

        tmp = defaultdict(list)
        max_seg_id = -1

        for i, row in enumerate(rows):
            fid = row["from_id"]
            tid = row["to_id"]

            self.from_ids.append(fid)
            self.to_ids.append(tid)
            self.from_strands.append(self.strand_map[row["from_strand"]])
            self.to_strands.append(self.strand_map[row["to_strand"]])

            tmp[fid].append(i)
            tmp[tid].append(i)
            max_seg_id = max(max_seg_id, fid, tid)

        for i in range(max_seg_id + 1):
            links = tmp.get(i, [])
            self.seg_index_offsets.append(len(self.seg_index_flat))
            self.seg_index_counts.append(len(links))
            self.seg_index_flat.extend(links)
        
        time_end = time.time()
        print(f"Loaded {len(rows)} links in {round(time_end - time_start, 2)} seconds.")

    def get_link_by_index(self, i, with_hap=False):
        link = {
            "from_id": self.from_ids[i],
            "from_strand": self.rev_strand_map[self.from_strands[i]],
            "to_id": self.to_ids[i],
            "to_strand": self.rev_strand_map[self.to_strands[i]],
        }

        if with_hap:
            self.cur.execute("""
                SELECT haplotype, reverse, frequency FROM links 
                WHERE from_id = ? AND to_id = ?
            """, (link["from_id"], link["to_id"]))
            row = self.cur.fetchone()
            link["haplotype"] = row["haplotype"]
            link["reverse"] = row["reverse"]
            link["frequency"] = row["frequency"]

        return link

    def get_haplotype_presence(self, link, sample_name):
        #todo: test and verify
        if isinstance(link, tuple):
            link = self.get_link(*link)
        if not link:
            return False
        hap_str = link.get("haplotype", "0")
        hap_int = int(hap_str, 16)
        sample_idx = self.sample_idx.get(sample_name)
        if sample_idx is None:
            return False
        return ((hap_int >> sample_idx) & 1) == 1
    
    def get_links_by_segment(self, seg_id):

        if seg_id >= len(self.seg_index_offsets) or seg_id < 0:
            return []

        offset = self.seg_index_offsets[seg_id]
        count = self.seg_index_counts[seg_id]

        return [self.get_link_by_index(self.seg_index_flat[offset + j]) for j in range(count)]
    
    def get_by_range(self, start_id, end_id):
        results = []
        for node_id in range(start_id, end_id + 1):
            results.extend(self.get_by_from_id(node_id))
        return results

    def close(self):
        self.conn.close()
