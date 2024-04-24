from db.neo4j_db import get_session
import uuid

def insert_subgraph(subgraph):
    if not subgraph:
        return

    subgraph_id = str(uuid.uuid4())

    with get_session() as (db,session):

        query = """
                CREATE (:Subgraph { 
                db: $db,
                id: $id })
                """
        session.run(query, parameters={"db": db, "id":subgraph_id})

        query = """
                UNWIND $graph AS node
                MATCH (s:Subgraph {id: $id, db: $db}), (n:Segment {db: $db, id: node})
                CREATE (n)-[:SUBGRAPH]->(s)
                """
        session.run(query, {"graph": list(subgraph["graph"]), "db": db,  "id":subgraph_id})

        query = """
                UNWIND $anchors AS anchor
                MATCH (s:Subgraph {id: $id, db: $db}), (n:Segment {db: $db, id: anchor})
                CREATE (s)-[:ANCHOR]->(n)
                """
        session.run(query, {"anchors": list(subgraph["anchor"]), "db": db,  "id":subgraph_id})
