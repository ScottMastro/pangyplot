from db.neo4j_db import get_session

def create_compact_links(merged_map):
    batch_size=100000

    links = []
    for compacted_id, original_ids in merged_map.items():
        for original_id in original_ids:
            links.append({"s1": original_id, "s2": compacted_id})

    with get_session(collection=True) as (db, collection, session):

        for i in range(0, len(links), batch_size):
            batch = links[i:i + batch_size]
            query = """
                    UNWIND $links AS link
                    MATCH (s1:Segment {db: $db, collection: $col, id: link.s1}), 
                          (s2:Segment {db: $db, collection: $col, id: link.s2})
                    MERGE (s1)-[:COMPACT]->(s2)
                    """
            session.run(query, {"links": batch, "col": collection, "db": db})
    

def annotate_deletions_simple():
    with get_session(collection=True) as (db, collection, session):
        query = """
        MATCH (s1:Segment)-[l:LINKS_TO]->(s2:Segment)
        WHERE s1.db = $db AND s1.collection = $col
        MATCH (s1)-[e1:END]->(b:Bubble)-[e2:END]->(s2)
        SET l.is_del = true
        """
        session.run(query, {"db": db, "col": collection})

def annotate_deletions():
    annotate_deletions_simple()
    
    # accounts for the fact that nodes can be compacted
    with get_session(collection=True) as (db, collection, session):
        query = """
                MATCH (s1:Segment)-[:COMPACT]-(s1c:Segment)
                MATCH (s1c)-[:END]-(b:Bubble)-[:END]-(s2:Segment)
                WHERE s1c.db = $db AND s1c.collection = $col
                MATCH (s1)-[l:LINKS_TO]-(s2)
                SET l.is_del = true
                """
        session.run(query, {"db": db, "col": collection})
        query = """
                MATCH (s1:Segment)-[:COMPACT]-(s1c:Segment),
                    (s2:Segment)-[:COMPACT]-(s2c:Segment)
                MATCH (s1c)-[:END]-(b:Bubble)-[:END]-(s2c)
                WHERE s1c.db = $db AND s1c.collection = $col
                MATCH (s1)-[l:LINKS_TO]-(s2)
                SET l.is_del = true
                """
        session.run(query, {"db": db, "col": collection})

def anchor_alternative_branches():
    with get_session(collection=True) as (db, collection, session):

        query = """
                MATCH (s1:Segment)<-[:ANCHOR]-(s:Subgraph)<-[:SUBGRAPH]-(s2:Segment)-[:INSIDE*]->(a)
                WHERE s.db = $db AND s.collection = $col AND a.start IS NULL 
                AND NOT EXISTS {
                    MATCH (a)-[:INSIDE]->(b)
                    WHERE b.start IS NULL
                }
                MERGE (a)-[:ANCHOR]->(s1)
                """
        session.run(query, {"db": db, "col": collection})
    
        query = """
                MATCH (s1:Segment)<-[:ANCHOR]-(s:Subgraph)<-[:SUBGRAPH]-(s2:Segment)
                WHERE s2.db = $db AND s2.collection = $col AND s2.start IS NULL
                AND NOT EXISTS {
                    MATCH (s2)-[:INSIDE]->()
                }
                MERGE (s2)-[:ANCHOR]->(s1)
                """
        session.run(query, {"db": db, "col": collection})

def adjust_compacted_nodes():
    with get_session(collection=True) as (db, collection, session):

        query = """
                MATCH (b:Bubble)-[r:END]-(e:Segment)<-[:COMPACT]-(c:Segment)-[:LINKS_TO]-(s:Segment)-[:INSIDE]->(b)
                WHERE b.db = $db AND b.collection = $col AND c <> e
                WITH DISTINCT b, r, c, startNode(r) AS from, endNode(r) AS to
                DELETE r
                FOREACH (_ IN CASE WHEN from = b THEN [1] ELSE [] END |
                    CREATE (b)-[:END]->(c)
                )
                FOREACH (_ IN CASE WHEN to = b THEN [1] ELSE [] END |
                    CREATE (c)-[:END]->(b)
                )
                """
        session.run(query, {"db": db, "col": collection})

        #TODO:
        #query = """
        #        MATCH (a:Chain)-[r:END]-(e:Segment)<-[:COMPACT]-(c:Segment)-[:CHAINED]-(s:Segment)-[:INSIDE]->(b)
        #        WHERE a.db = $db AND c <> e
        #        WITH DISTINCT b, r, c, startNode(r) AS from, endNode(r) AS to
        #        DELETE r
        #        FOREACH (_ IN CASE WHEN from = b THEN [1] ELSE [] END |
        #            CREATE (a)-[:CHAIN_END]->(c)
        #        )
        #        FOREACH (_ IN CASE WHEN to = b THEN [1] ELSE [] END |
        #            CREATE (c)-[:CHAIN_END]->(a)
        #        )
        #        """
        #session.run(query, {"db": db})