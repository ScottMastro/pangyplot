from db.neo4j_db import get_session

def insert_bubble_nodes(session, bubbles, batch_size):
    for i in range(0, len(bubbles), batch_size):
        batch = bubbles[i:i + batch_size]
        print(f"{i}/{len(bubbles)} bubbles inserted.")
        query = """
                UNWIND $bubbles AS bubble
                CREATE (:Bubble {id: bubble.id, subtype: bubble.type})
                """
        session.run(query, {"bubbles": batch})

def create_links(session, links, relationship, direction):
    a = direction if direction == "<-" else "-"
    b = direction if direction == "->" else "-"

    query = """
            UNWIND $links AS link
            MATCH (s:Segment {id: link.sid}), (b:Bubble {id: link.bid}) 
            """ + f" CREATE (s){a}[:{relationship}]{b}(b)"
            
    session.run(query, {"links": links})

def link_bubble_links(session, bubbles, batch_size):
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
        create_links(session, batch, "END", "->",) #s->b

    for i in range(0, len(endLinks), batch_size):
        batch = endLinks[i:i + batch_size]
        create_links(session, batch, "END", "<-") #s<-b

    for i in range(0, len(insideLinks), batch_size):
        batch = insideLinks[i:i + batch_size]
        create_links(session, batch, "INSIDE", "->") #s->b

def insert_bubbles(bubbles, batch_size=10000):
    if len(bubbles) == 0: return

    with get_session() as session:
        insert_bubble_nodes(session, bubbles, batch_size)
        link_bubble_links(session, bubbles, batch_size)


def add_bubble_properties():
    with get_session() as session:
        MATCH = "MATCH (s:Segment)-[r:INSIDE]->(b:Bubble) "

        q1= MATCH + " WITH b, MIN(s.start) AS start SET b.start = start"
        q2= MATCH + " WITH b, MAX(s.end) AS end SET b.end = end"
        q3= MATCH + " WITH b, SUM(s.length) AS size SET b.size = size"
        q4= MATCH + " WITH b, SUM(1) AS n SET b.n = n"
        q5= MATCH + " WITH b, COLLECT(DISTINCT s.chrom)[0] AS chrom SET b.chrom = chrom"

        print("Calculating bubble properties...")
        for query in [q1,q2,q3,q4,q5]:
            print(query)
            session.run(query)

        def layout_query(a,b):
            c = "MIN" if b=="1" else "MAX"
            d = "<" if b=="1" else ">"
            return MATCH + f"""
                WITH b, {c}(s.{a}1) AS p, {c}(s.{a}2) AS q
                WITH b, CASE WHEN p {d} q THEN p ELSE q END AS r
                SET b.{a}{b} = r
                """
        
        q6 = layout_query("x","1")
        q7 = layout_query("x","2")
        q8 = layout_query("y","1")
        q9 = layout_query("y","2")

        q10 = MATCH + """
        WITH b, SUM(s.x1) AS x1, SUM(s.x2) AS x2, SUM(2) AS n
        WITH b, (x1+x2)/n AS x
        SET b.x = x
        """
        q11 = MATCH + """
        WITH b, SUM(s.y1) AS y1, SUM(s.y2) AS y2, SUM(2) AS n
        WITH b, (y1+y2)/n AS y
        SET b.y = y
        """

        print("Calculating bubble layout...")
        for query in [q6,q7,q8,q9,q10,q11]:
            print(query)
            session.run(query)

