from db.neo4j_db import get_session

def add_chain_subtype():
    with get_session() as (db, session):
        query = """
        MATCH (b:Bubble)-[r:INSIDE]->(c:Chain)
        WHERE b.db = $db
        WITH c, 
            CASE WHEN ANY(bubble IN collect(b) WHERE bubble.subtype = "super") THEN "super" 
                ELSE "simple" 
            END as subtype
        SET c.subtype = subtype
        """
        session.run(query, {"db": db})

def connect_bubble_ends_to_chain():
    with get_session() as (db, session):
        query = """
                MATCH (s:Segment)-[:END]-(b:Bubble)-[:INSIDE]->(c:Chain)
                WHERE s.db = $db AND NOT (c)-[:END]-(s) 
                MERGE (s)-[:INSIDE]->(c)
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

def annotate_deletions():
    with get_session() as (db, session):
        query = """
        MATCH (s1:Segment)-[l:LINKS_TO]->(s2:Segment)
        WHERE s1.db = $db AND s2.db = $db
        MATCH (s1)-[e1:END]->(b:Bubble)-[e2:END]->(s2)
        SET l.isDel = true
        """
        session.run(query, {"db": db})
