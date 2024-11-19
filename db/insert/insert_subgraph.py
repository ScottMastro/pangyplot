from db.neo4j_db import get_session
import uuid

def insert_subgraph(subgraph, batch_size=1000):
    if not subgraph:
        return

    subgraph_id = str(uuid.uuid4())
    with get_session() as (db, session):

        # Create the Subgraph node
        query = """
                CREATE (:Subgraph { 
                db: $db,
                id: $id })
                """
        session.run(query, parameters={"db": db, "id": subgraph_id})

        # Insert graph nodes in batches
        graph_nodes = list(subgraph["graph"])
        for i in range(0, len(graph_nodes), batch_size):
            batch = graph_nodes[i:i + batch_size]

            session.run("""
                UNWIND $batch AS node
                MATCH (s:Subgraph {db: $db, id: $id}),
                      (n:Segment {db: $db, id: node})
                CREATE (n)-[:SUBGRAPH]->(s)
            """, parameters={"batch": batch, "id": subgraph_id, "db": db})

        # Insert anchor nodes in batches
        anchor_nodes = list(subgraph["anchor"])
        for i in range(0, len(anchor_nodes), batch_size):
            batch = anchor_nodes[i:i + batch_size]
            session.run("""
                UNWIND $batch AS anchor
                MATCH (s:Subgraph {db: $db, id: $id}),
                      (n:Segment {db: $db, id: anchor})
                CREATE (s)-[:ANCHOR]->(n)
            """, parameters={"batch": batch, "id": subgraph_id, "db": db})