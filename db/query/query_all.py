from db.neo4j_db import get_session

def query_all_segments():
    batch_size=100000
    nodes = []

    with get_session() as session:
        skip = 0
        while True:
            query = """
                    MATCH (s:Segment)
                    RETURN s.id, s.length
                    SKIP $skip
                    LIMIT $limit
                    """
            results = session.run(query, skip=skip, limit=batch_size)
            batch = [(result['s.id'], result['s.length']) for result in results]

            if not batch:
                break
            nodes.extend(batch)
            skip += batch_size
    return nodes

def query_all_links():
    batch_size=100000
    links = []
    with get_session() as session:
        skip = 0
        while True:
            query = """
                    MATCH (s1:Segment)-[l:LINKS_TO]->(s2:Segment)
                    RETURN l.from_strand, l.to_strand, s1.id, s2.id
                    SKIP $skip
                    LIMIT $limit
                    """
            results = session.run(query, skip=skip, limit=batch_size)
            batch = [(result['l.from_strand'], result['s1.id'], result['l.to_strand'], result['s2.id']) for result in results]
    
            if not batch:
                break 
            
            links.extend(batch)
            skip += batch_size

    return links
