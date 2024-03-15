from db.neo4j_db import get_session

def query_all_segments():
    batch_size=100000
    nodes = []

    with get_session() as (db,session):
        skip = 0
        while True:
            query = """
                    MATCH (s:Segment)
                    WHERE s.db = $db
                    RETURN s.id, s.length
                    SKIP $skip
                    LIMIT $limit
                    """
            results = session.run(query, parameters={"db": db}, skip=skip, limit=batch_size)
            batch = [(result['s.id'], result['s.length']) for result in results]

            if not batch:
                break
            nodes.extend(batch)
            skip += batch_size
    return nodes

def query_all_links():
    batch_size=100000
    links = []
    with get_session() as (db,session):
        skip = 0
        while True:
            query = """
                    MATCH (s1:Segment)-[l:LINKS_TO]->(s2:Segment)
                    WHERE s1.db = $db
                    RETURN l.from_strand, l.to_strand, s1.id, s2.id
                    SKIP $skip
                    LIMIT $limit
                    """
            results = session.run(query, parameters={"db": db}, skip=skip, limit=batch_size)
            batch = [(result['l.from_strand'], result['s1.id'], result['l.to_strand'], result['s2.id']) for result in results]
    
            if not batch:
                break 
            
            links.extend(batch)
            skip += batch_size

    return links

def query_all_chromosomes():
    with get_session() as (db, session):
        query = "MATCH (s:Segment) WHERE s.db = $db RETURN DISTINCT s.chrom"
        result = session.run(query, parameters={"db": db})
        chromosomes = [record["s.chrom"] for record in result if record["s.chrom"] is not None]

    return chromosomes

def query_all_db():
    with get_session() as (_, session):
        query = "MATCH (s:Segment) RETURN DISTINCT s.db"
        result = session.run(query)
        dbs = [record["s.db"] for record in result if record["s.db"] is not None]

    return dbs
