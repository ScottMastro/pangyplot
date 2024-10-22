from db.neo4j_db import get_session

def insert_samples(samples):
    if len(samples) == 0: return
    with get_session() as (db, session):
        query = """
            UNWIND $samples AS sample
            CREATE (:Sample {
                db: $db,
                id: sample.id,
                index: sample.idx
            })
        """
        session.run(query, parameters={"samples": samples, "db": db})