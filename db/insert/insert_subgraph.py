from db.neo4j_db import get_session
import uuid

def insert_subgraphs_slow(subgraphs, subgraph_type="alt", batch_size=1000):

    with get_session(collection=True) as (db, collection, session):

        for subgraph in subgraphs:
            subgraph_id = str(uuid.uuid4())

            # Create the Subgraph node
            query = """
                    CREATE (:Subgraph { 
                    db: $db,
                    collection: $col,
                    type: $type,
                    id: $id })
                    """
            session.run(query, parameters={"col": collection, "db": db, "id": subgraph_id, "type": subgraph_type})

            # Insert graph nodes in batches
            graph_nodes = list(subgraph["graph"])
            for i in range(0, len(graph_nodes), batch_size):
                batch = graph_nodes[i:i + batch_size]

                session.run("""
                    UNWIND $batch AS node
                    MATCH (s:Subgraph {db: $db, collection: $col, id: $id}),
                        (n:Segment {db: $db, collection: $col, id: node})
                    CREATE (n)-[:SUBGRAPH]->(s)
                """, parameters={"col": collection, "batch": batch, "id": subgraph_id, "db": db})

            # Insert anchor nodes in batches
            anchor_nodes = list(subgraph["anchor"])
            for i in range(0, len(anchor_nodes), batch_size):
                batch = anchor_nodes[i:i + batch_size]
                session.run("""
                    UNWIND $batch AS anchor
                    MATCH (s:Subgraph {db: $db, collection: $col, id: $id}),
                        (n:Segment {db: $db, collection: $col, id: anchor})
                    CREATE (s)-[:ANCHOR]->(n)
                """, parameters={"col": collection, "batch": batch, "id": subgraph_id, "db": db})

def insert_subgraphs(subgraphs, subgraph_type="alt", batch_size=10000):
    with get_session(collection=True) as (db, collection, session):
        # 1. Build and batch-create all Subgraph nodes
        subgraph_rows = []
        for sg in subgraphs:
            subgraph_rows.append({
                "db": db,
                "col": collection,
                "sgid": str(uuid.uuid4()),
                "type": subgraph_type
            })

        for i in range(0, len(subgraph_rows), batch_size):
            chunk = subgraph_rows[i : i + batch_size]
            session.run("""
                UNWIND $chunk AS row
                CREATE (:Subgraph {
                    db: row.db,
                    collection: row.col,
                    id: row.sgid,
                    type: row.type
                })
            """, {"chunk": chunk})

        # 2. Flatten out graph‐edges and anchor‐edges separately
        graph_rels  = []
        anchor_rels = []
        for sg_row, sg in zip(subgraph_rows, subgraphs):
            sgid = sg_row["sgid"]
            for segment_id in sg["graph"]:
                graph_rels.append({
                    "db": db,
                    "col": collection,
                    "sgid": sgid,
                    "sid": segment_id
                })
            for segment_id in sg["anchor"]:
                anchor_rels.append({
                    "db": db,
                    "col": collection,
                    "sgid": sgid,
                    "sid": segment_id
                })

        # 3. Batch-create SUBGRAPH relationships
        for i in range(0, len(graph_rels), batch_size):
            chunk = graph_rels[i : i + batch_size]
            session.run("""
                UNWIND $chunk AS row
                MATCH 
                  (s:Subgraph {db: row.db, collection: row.col, id: row.sgid}),
                  (n:Segment  {db: row.db, collection: row.col, id: row.sid})
                CREATE (n)-[:SUBGRAPH]->(s)
            """, {"chunk": chunk})

        # 4. Batch-create ANCHOR relationships
        for i in range(0, len(anchor_rels), batch_size):
            chunk = anchor_rels[i : i + batch_size]
            session.run("""
                UNWIND $chunk AS row
                MATCH 
                  (s:Subgraph {db: row.db, collection: row.col, id: row.sgid}),
                  (n:Segment  {db: row.db, collection: row.col, id: row.sid})
                CREATE (s)-[:ANCHOR]->(n)
            """, {"chunk": chunk})
