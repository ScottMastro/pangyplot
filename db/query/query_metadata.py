from db.neo4j_db import get_session

def query_samples():
    with get_session() as (db, session):
        query = """
            MATCH (s:Sample {db: $db})
            RETURN s.id AS id, s.index AS idx
        """
        result = session.run(query, parameters={"db": db})
        samples = [{"id": record["id"], "index": record["idx"]} for record in result]
        
        return samples
    return []

def query_collections():
    with get_session() as (db, session):
        query = """
            MATCH (c:Collection {db: $db})
            RETURN c
        """
        result = session.run(query, parameters={"db": db})
        collections = [dict(record["c"].items()) for record in result]
        return collections
    return []

