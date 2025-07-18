import os
import sqlite3
import json
from preprocess2.bubble.BubbleData import BubbleData

NAME = "bubbles.db"

def get_connection(chr_dir):
    db_path = os.path.join(chr_dir, NAME)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def _remove_if_exists(chr_dir):
    db_path = os.path.join(chr_dir, NAME)
    if os.path.exists(db_path):
        os.remove(db_path)

def create_bubble_tables(chr_dir):
    _remove_if_exists(chr_dir)
    conn = get_connection(chr_dir)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE bubbles (
            id INTEGER PRIMARY KEY,
            chain TEXT,
            type TEXT,
            parent INTEGER,
            children TEXT,
            siblings TEXT,
            source INTEGER,
            compacted_source TEXT,
            sink INTEGER,
            compacted_sink TEXT,
            inside TEXT,
            range_exclusive TEXT,
            range_inclusive TEXT,
            length INTEGER,
            gc_count INTEGER,
            n_counts INTEGER
        );
    """)

    conn.commit()
    return conn

def _insert_bubble(cur, bubble):
    cur.execute("""
        INSERT INTO bubbles (
            id, chain, type, parent,
            children, siblings,
            source, compacted_source, sink, compacted_sink,
            inside, range_exclusive, range_inclusive,
            length, gc_count, n_counts
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        bubble.id,
        bubble.chain,
        bubble.type,
        bubble.parent,
        json.dumps(bubble.children),
        json.dumps(bubble._siblings),
        bubble._source,
        json.dumps(bubble._compacted_source),
        bubble._sink,
        json.dumps(bubble._compacted_sink),
        json.dumps(sorted(bubble.inside)),  # Convert set to list
        json.dumps(bubble._range_exclusive),
        json.dumps(bubble._range_inclusive),
        bubble.length,
        bubble.gc_count,
        bubble.n_counts
    ))

def insert_bubbles(conn, bubbles):
    cur = conn.cursor()
    for bubble in bubbles:
        _insert_bubble(cur, bubble)
    conn.commit()

def load_bubble(row):
    bubble = BubbleData()
    bubble.id = row["id"]
    bubble.chain = row["chain"]
    bubble.type = row["type"]
    bubble.parent = row["parent"]
    bubble.children = json.loads(row["children"])
    bubble._siblings = json.loads(row["siblings"])
    bubble._source = row["source"]
    bubble._compacted_source = json.loads(row["compacted_source"])
    bubble._sink = row["sink"]
    bubble._compacted_sink = json.loads(row["compacted_sink"])
    bubble.inside = set(json.loads(row["inside"]))
    bubble._range_exclusive = json.loads(row["range_exclusive"])
    bubble._range_inclusive = json.loads(row["range_inclusive"])
    bubble.length = row["length"]
    bubble.gc_count = row["gc_count"]
    bubble.n_counts = row["n_counts"]
    return bubble
