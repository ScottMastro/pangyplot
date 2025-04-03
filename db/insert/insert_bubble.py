from db.neo4j_db import get_session

def insert_bubble_nodes(db, session, bubbles, batch_size):
    for i in range(0, len(bubbles), batch_size):
        batch = bubbles[i:i + batch_size]
        print(f"{i}/{len(bubbles)} bubbles inserted.")
        query = """
                UNWIND $bubbles AS bubble
                CREATE (:Bubble {db: $db, id: bubble.id, subtype: bubble.type})
                """
        session.run(query, {"bubbles": batch, "db": db})

def create_links(db, session, links, relationship, direction):
    a = direction if direction == "<-" else "-"
    b = direction if direction == "->" else "-"

    query = """
            UNWIND $links AS link
            MATCH (s:Segment {db: $db, id: link.sid}), (b:Bubble {db: $db, id: link.bid})
            """ + f" CREATE (s){a}[:{relationship}]{b}(b)"
            
    session.run(query, {"links": links, "db": db})

def link_bubble_links(db, session, bubbles, batch_size):
    startLinks,endLinks,insideLinks = [],[],[]

    for bubble in bubbles:
        start_id, end_id = bubble["ends"]
        bubble_id = bubble["id"]
        startLinks.append({"sid": start_id, "bid": bubble_id})
        endLinks.append({"sid": end_id, "bid": bubble_id})
        for segment_id in bubble["inside"]:
            insideLinks.append({"sid": segment_id, "bid": bubble_id})

    for i in range(0, len(startLinks), batch_size):
        batch = startLinks[i:i + batch_size]
        create_links(db, session, batch, "END", "->",) #s->b

    for i in range(0, len(endLinks), batch_size):
        batch = endLinks[i:i + batch_size]
        create_links(db, session, batch, "END", "<-") #s<-b

    for i in range(0, len(insideLinks), batch_size):
        batch = insideLinks[i:i + batch_size]
        create_links(db, session, batch, "INSIDE", "->") #s->b

def insert_bubbles(bubbles, batch_size=10000):
    if len(bubbles) == 0: return

    with get_session() as (db, session):
        insert_bubble_nodes(db, session, bubbles, batch_size)
        link_bubble_links(db, session, bubbles, batch_size)


def add_bubble_properties():
    with get_session() as (db, session):

        MATCH = "MATCH (s:Segment)-[r:INSIDE]->(b:Bubble) WHERE b.db = $db"
        q1= MATCH + " WITH b, MIN(s.start) AS start SET b.start = start"
        q2= MATCH + " WITH b, MAX(s.end) AS end SET b.end = end"
        q3= MATCH + " WITH b, SUM(s.length) AS size SET b.size = size"
        q4= MATCH + " WITH b, MAX(s.length) AS largest SET b.largest_child = largest"
        q5= MATCH + " WITH b, SUM(1) AS n SET b.n = n"
        q6= MATCH + " WITH b, COLLECT(DISTINCT s.chrom)[0] AS chrom SET b.chrom = chrom"
        q7= MATCH + " WITH b, COLLECT(DISTINCT s.genome)[0] AS genome SET b.genome = genome"
        q8= MATCH + " WITH b, ANY(s IN COLLECT(s.is_ref) WHERE s = true) AS hasRef SET b.is_ref = hasRef"
        q9= MATCH + " WITH b, SUM(s.gc_count) AS count SET b.gc_count = count"

        print("Calculating bubble properties...")
        for query in [q1,q2,q3,q4,q5,q6,q7,q8,q9]:
            print(query)
            session.run(query, {"db": db})

    with get_session() as (db, session):

        MATCH = """
            MATCH (x)-[:INSIDE]->(b:Bubble)<-[r:END]-(s:Segment)
            WHERE b.db = $db AND exists((x)-[]-(s))
        """
        q1= MATCH + " WITH b, avg(x.x1) AS avgX1 SET b.x1 = avgX1"
        q2= MATCH + " WITH b, avg(x.y1) AS avgY1 SET b.y1 = avgY1"
        q3= MATCH + " WITH b, avg(x.x2) AS avgX2 SET b.x2 = avgX2"
        q4= MATCH + " WITH b, avg(x.y2) AS avgY2 SET b.y2 = avgY2"

        print("Calculating bubble layout...")
        for query in [q1,q2,q3,q4]:
            print(query)
            session.run(query, {"db": db})

    with get_session() as (db, session):

        MATCH = """
                MATCH (e1:Segment)-[:END]->(b:Bubble)-[:END]->(e2:Segment)
                WHERE e1.db = $db AND e2.db = $db""" + \
                " AND e1.genome = e2.genome" + \
                " AND e1.chrom IS NOT NULL AND e2.chrom IS NOT NULL AND b.chrom is NULL"

        q1 = MATCH + " SET b.start = CASE WHEN e1.end < e2.end THEN e1.end + 1 ELSE e2.end + 1 END"
        q2 = MATCH + " SET b.end = CASE WHEN e1.start > e2.start THEN e1.start - 1 ELSE e2.start - 1 END"
        q3 = MATCH + " SET b.genome = e1.genome"
        q4 = MATCH + " SET b.chrom = e1.chrom"

        print("Calculating chain properties...")
        for query in [q1,q2,q3,q4]:
            print(query)
            session.run(query, {"db": db})