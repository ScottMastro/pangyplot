import json
import gzip
from db.neo4j_db import db_init, get_session

def import_dataset(input_path, batch_size=10000):
    db_init(None)

    open_func = gzip.open if input_path.endswith(".gz") else open

    print("  Uploading data...")

    def batched_iter(file):
        batch = []
        for line in file:
            if line.strip():
                batch.append(json.loads(line))
                if len(batch) >= batch_size:
                    yield batch
                    batch = []
        if batch:
            yield batch

    with get_session() as (_, session), open_func(input_path, "rt") as f:
        count = 0
        for batch in batched_iter(f):
            nodes = [item for item in batch if item["type"] == "node"]
            if not nodes:
                continue

            label_groups = {}
            for node in nodes:
                labels = ":".join(node["labels"])
                label_groups.setdefault(labels, []).append(node)

            for labels, group in label_groups.items():
                session.run(
                    f"""
                    UNWIND $batch AS row
                    MERGE (n:{labels} {{id: row.id, db: row.db}})
                    SET n += row.props
                    """,
                    batch=[{
                        "id": n["properties"]["id"],
                        "db": n["properties"]["db"],
                        "props": n["properties"]
                    } for n in group]
                )

            count += len(nodes)
            print(f"\r  📁 {count} nodes imported...", end="", flush=True)
        print(f"\r  📁 {count} nodes imported.       ")


    with get_session() as (_, session), open_func(input_path, "rt") as f:
        count = 0
        for batch in batched_iter(f):
            rels = [item for item in batch if item["type"] == "relationship"]
            if not rels:
                continue
            for rel in rels:
                session.run("""
                    MATCH (a), (b)
                    WHERE a.id = $start AND b.id = $end
                    CREATE (a)-[r:%s]->(b) SET r = $props
                """ % rel["rel_type"], {
                    "start": rel["start"],
                    "end": rel["end"],
                    "props": rel["properties"]
                })
            count += len(rels)
            print(f"\r  🗃️ {count} relationships imported...", end="", flush=True)
        print(f"\r  🗃️ {count} relationships imported.       ")

    print(f"\n  Import complete: {input_path}")


def export_database(db_name, output_prefix, collection=None, batch_size=100000):
    db_init(db_name)
    output_path = f"{output_prefix}.txt.gz"

    data = {"nodes": [], "relationships": []}

    with get_session() as (db, session), gzip.open(output_path, "wt") as f:
        
        result = session.run(f"""
            MATCH (n:Sample) WHERE n.db = $db
            RETURN id(n) as id, labels(n) as labels, properties(n) as props
        """, db=db)

        for record in result:
            f.write(json.dumps({
                "type": "node",
                "id": record["id"],
                "labels": record["labels"],
                "properties": record["props"]
            }) + "\n")
        print("  👤 Sample nodes exported")

        # Export nodes
        offset = 0
        while True:
            result = session.run("""
                MATCH (n)
                WHERE n.db = $db AND NOT 'Sample' IN labels(n)
                      AND ($collection IS NULL OR n.collection = $collection)
                RETURN id(n) as id, labels(n) as labels, properties(n) as props
                SKIP $offset LIMIT $batch
            """, db=db_name, collection=int(collection), offset=offset, batch=batch_size)
            nodes = result.data()
            if not nodes:
                break
            for record in nodes:
                f.write(json.dumps({
                    "type": "node",
                    "id": record["id"],
                    "labels": record["labels"],
                    "properties": record["props"]
                }) + "\n")
            offset += batch_size
            print(f"\r  📄 {offset} nodes exported...", end="", flush=True)
        print(f"\r  📄 {offset} nodes exported.       ")

        # Export relationships
        offset = 0
        while True:
            result = session.run("""
                MATCH (a)-[r]->(b)
                WHERE a.db = $db AND ($collection IS NULL OR a.collection = $collection)
                RETURN id(r) as id, id(a) as start_id, id(b) as end_id, type(r) as type, properties(r) as props
                SKIP $offset LIMIT $batch
            """, db=db_name, collection=int(collection), offset=offset, batch=batch_size)
            rels = result.data()
            if not rels:
                break
            for record in rels:
                f.write(json.dumps({
                    "type": "relationship",
                    "id": record["id"],
                    "start": record["start_id"],
                    "end": record["end_id"],
                    "rel_type": record["type"],
                    "properties": record["props"]
                }) + "\n")
            offset += batch_size
            print(f"\r  📑 {offset} relationships exported...", end="", flush=True)
        print(f"\r  📑 {offset} relationships exported.       ")

    print(f"  Export complete: {output_path}")

