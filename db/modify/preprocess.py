from db.neo4j_db import get_session
import sys, time

def query_segment_summary():
    batch_size=100000
    nodes = []
    startTime = time.time()

    with get_session() as (db, session):
        skip = 0
        while True:
            query = """
                    MATCH (s:Segment)
                    WHERE s.db = $db
                    RETURN s.id, s.length, s.start
                    SKIP $skip
                    LIMIT $limit
                    """
            results = session.run(query, parameters={"db": db}, skip=skip, limit=batch_size)
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

def query_link_summary():
    batch_size=100000
    links = []
    startTime = time.time()
    
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
    
            elapsed = time.time() - startTime
            rate = len(links) / elapsed if elapsed > 0 else 0
            sys.stdout.write(f"\r      Read {len(links):,} segments at {rate:,.1f}/sec.")

    print()
    return links

def create_compact_links(merged_map):
    batch_size=100000

    links = []
    for compacted_id, original_ids in merged_map.items():
        for original_id in original_ids:
            links.append({"s1": original_id, "s2": compacted_id})

    with get_session() as (db, session):

        for i in range(0, len(links), batch_size):
            batch = links[i:i + batch_size]
            query = """
                    UNWIND $links AS link
                    MATCH (s1:Segment {db: $db, id: link.s1}), (s2:Segment {db: $db, id: link.s2})
                    MERGE (s1)-[:COMPACT]->(s2)
                    """
            session.run(query, {"links": batch, "db": db})
    

def annotate_deletions_simple():
    with get_session() as (db, session):
        query = """
        MATCH (s1:Segment)-[l:LINKS_TO]->(s2:Segment)
        WHERE s1.db = $db AND s2.db = $db
        MATCH (s1)-[e1:END]->(b:Bubble)-[e2:END]->(s2)
        SET l.is_del = true
        """
        session.run(query, {"db": db})

def annotate_deletions():
    annotate_deletions_simple()
    
    # accounts for the fact that nodes can be compacted
    with get_session() as (db, session):
        query = """
                MATCH (s1:Segment)-[:COMPACT]-(s1c:Segment)
                MATCH (s1c)-[:END]-(b:Bubble)-[:END]-(s2:Segment)
                WHERE s1c.db = $db AND s2.db = $db
                MATCH (s1)-[l:LINKS_TO]-(s2)
                SET l.is_del = true
                """
        session.run(query, {"db": db})
        query = """
                MATCH (s1:Segment)-[:COMPACT]-(s1c:Segment),
                    (s2:Segment)-[:COMPACT]-(s2c:Segment)
                MATCH (s1c)-[:END]-(b:Bubble)-[:END]-(s2c)
                WHERE s1c.db = $db AND s2c.db = $db
                MATCH (s1)-[l:LINKS_TO]-(s2)
                SET l.is_del = true
                """
        session.run(query, {"db": db})

def anchor_alternative_branches():
    with get_session() as (db, session):

        query = """
                MATCH (s1:Segment)<-[:ANCHOR]-(s:Subgraph)<-[:SUBGRAPH]-(s2:Segment)-[:INSIDE*]->(a)
                WHERE s.db = $db AND a.start IS NULL 
                AND NOT EXISTS {
                    MATCH (a)-[:INSIDE]->(b)
                    WHERE b.start IS NULL
                }
                MERGE (a)-[:ANCHOR]->(s1)
                """
        session.run(query, {"db": db})
    
        query = """
                MATCH (s1:Segment)<-[:ANCHOR]-(s:Subgraph)<-[:SUBGRAPH]-(s2:Segment)
                WHERE s.db = $db AND s2.start IS NULL
                AND NOT EXISTS {
                    MATCH (s2)-[:INSIDE]->()
                }
                MERGE (s2)-[:ANCHOR]->(s1)
                """
        session.run(query, {"db": db})




