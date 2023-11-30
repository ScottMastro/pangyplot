from db.db import get_session

def add_chain_subtype():
    with get_session() as session:
        query = """
        MATCH (b:Bubble)-[r:INSIDE]->(c:Chain)
        WITH c, 
            CASE WHEN ANY(bubble IN collect(b) WHERE bubble.subtype = "super") THEN "super" 
                ELSE "simple" 
            END as subtype
        SET c.subtype = subtype
        """
        session.run(query)

def connect_bubble_ends_to_chain():
    with get_session() as session:
        query = """
                MATCH (s:Segment)-[:END]-(b:Bubble)-[:INSIDE]->(c:Chain)
                WHERE NOT (c)-[:END]-(s)
                MERGE (s)-[:INSIDE]->(c)
                """
        session.run(query)

def add_null_nodes():
    with get_session() as session:

        query = """
                MATCH (s1:Segment)-[l:LINKS_TO]->(s2:Segment)
                MATCH (s1)-[e1:END]->(b:Bubble)-[e2:END]->(s2)
                CREATE (s3:Segment {
                    id: s1.id + '_' + s2.id,
                    sequence: "",
                    length: 0,
                    x1: s1.x2,
                    y1: s1.y2,
                    x2: s2.x1,
                    y2: s2.y1
                })
                CREATE (s1)-[:LINKS_TO]->(s3)-[:LINKS_TO]->(s2)
                CREATE (s3)-[:INSIDE]->(b)
                DELETE l
                """

        session.run(query)
