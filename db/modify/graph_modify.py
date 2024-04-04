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

def add_null_nodes():
    with get_session() as (db, session):

        query = """
                MATCH (s1:Segment)-[l:LINKS_TO]->(s2:Segment)
                WHERE s1.db = $db
                MATCH (s1)-[e1:END]->(b:Bubble)-[e2:END]->(s2)
                CREATE (s3:Segment {
                    db: $db,
                    id: s1.id + '_' + s2.id,
                    sequence: "",
                    length: 0,
                    x1: s1.x2,
                    y1: s1.y2,
                    x2: s2.x1,
                    y2: s2.y1,
                    start: CASE WHEN s1.start < s2.start THEN s1.start ELSE s2.start END,
                    end: CASE WHEN s1.end < s2.end THEN s1.end ELSE s2.end END,
                    genome: COALESCE(s1.genome, s2.genome),
                    chrom: COALESCE(s1.chrom, s2.chrom),
                    tag: "null"
                })
                CREATE (s1)-[:LINKS_TO]->(s3)-[:LINKS_TO]->(s2)
                CREATE (s3)-[:INSIDE]->(b)
                DELETE l
                """

        session.run(query, {"db": db})
