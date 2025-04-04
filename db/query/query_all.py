from db.neo4j_db import get_session

def query_all_chromosomes():
    with get_session() as (db, session):
        query = "MATCH (s:Segment) WHERE s.db = $db RETURN DISTINCT s.chrom"
        result = session.run(query, parameters={"db": db})
        chromosomes = [record["s.chrom"] for record in result if record["s.chrom"] is not None]

    return chromosomes

def query_all_samples():
    with get_session() as (db, session):
        query = """
            MATCH (s:Sample {db: $db})
            RETURN s.id AS id, s.index AS idx
        """
        result = session.run(query, parameters={"db": db})
        samples = [{"id": record["id"], "index": record["idx"]} for record in result]
        
        return samples
    return []

def query_all_db():
    with get_session() as (_, session):
        query = "MATCH (s:Segment) RETURN DISTINCT s.db"
        result = session.run(query)
        dbs = [record["s.db"] for record in result if record["s.db"] is not None]

    return dbs

def query_all_genome():
    with get_session() as (db, session):
        query = """
        MATCH (s:Segment)
        WHERE s.db = $db
        RETURN s.genome AS genome, COUNT(*) AS count
        ORDER BY count DESC
        LIMIT 1
        """
        result = session.run(query, parameters={"db": db})
        record = result.single()
        return record["genome"] if record else None

