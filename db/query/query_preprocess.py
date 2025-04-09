from db.neo4j_db import get_session
import sys, time

def all_segment_summary():
    batch_size=100000
    nodes = []
    startTime = time.time()

    with get_session(collection=True) as (db, collection, session):
        skip = 0
        while True:
            query = """
                    MATCH (s:Segment)
                    WHERE s.db = $db AND s.collection = $col
                    RETURN s.id, s.length, s.start
                    SKIP $skip
                    LIMIT $limit
                    """
            results = session.run(query, parameters={"db": db, "col": collection}, skip=skip, limit=batch_size)
            batch = [(result['s.id'], result['s.length'], result["s.start"] is not None) for result in results]

            if not batch:
                break
            nodes.extend(batch)
            skip += batch_size
            
            elapsed = time.time() - startTime
            rate = len(nodes) / elapsed if elapsed > 0 else 0
            sys.stdout.write(f"\r      Read {len(nodes):,} segments at {rate:,.1f}/sec.")
    
    print()
    return nodes

def all_link_summary():
    batch_size=100000
    links = []
    startTime = time.time()
    
    with get_session(collection=True) as (db, collection, session):
        skip = 0
        while True:
            query = """
                    MATCH (s1:Segment)-[l:LINKS_TO]->(s2:Segment)
                    WHERE s1.db = $db AND s1.collection = $col
                    RETURN l.from_strand, l.to_strand, s1.id, s2.id
                    SKIP $skip
                    LIMIT $limit
                    """
            results = session.run(query, parameters={"db": db, "col": collection}, skip=skip, limit=batch_size)
            batch = [(result['l.from_strand'], result['s1.id'], result['l.to_strand'], result['s2.id']) for result in results]
    
            if not batch:
                break 
            
            links.extend(batch)
            skip += batch_size
    
            elapsed = time.time() - startTime
            rate = len(links) / elapsed if elapsed > 0 else 0
            sys.stdout.write(f"\r      Read {len(links):,} segments at {rate:,.1f}/sec.")

    print()
    return links
