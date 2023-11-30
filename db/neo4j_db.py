from db.db import get_session

def add_bubbles(bubbles, batch_size=10000):
    
    if len(bubbles) == 0: return
    with get_session() as session:

        for i in range(0, len(bubbles), batch_size):
            batch = bubbles[i:i + batch_size]

            print(i, "/", len(bubbles), "bubbles")
            query = """
            UNWIND $bubbles AS bubble
            CREATE (:Bubble {id: bubble.id, subtype: bubble.type})
            """
            session.run(query, {"bubbles": batch})

        startLinks = []
        endLinks = []
        insideLinks = []
        for bubble in bubbles:
            start,end = bubble["ends"]
            bid = bubble["id"]
            startLinks.append({"sid": start, "bid": bid})
            endLinks.append({"sid": end, "bid": bid})

            for sid in bubble["inside"]:
                insideLinks.append({"sid": sid, "bid": bid})

        for i in range(0, len(startLinks), batch_size):
            batch = startLinks[i:i + batch_size]

            print(i, "/", len(startLinks), "start links")
            query = """
            UNWIND $links AS link
            MATCH (b:Bubble {id: link.bid}), (s:Segment {id: link.sid})
            CREATE (b)-[:END]->(s)
            """
            session.run(query, {"links": batch})

        for i in range(0, len(endLinks), batch_size):
            batch = endLinks[i:i + batch_size]

            print(i, "/", len(endLinks), "end links")
            query = """
            UNWIND $links AS link
            MATCH (b:Bubble {id: link.bid}), (s:Segment {id: link.sid})
            CREATE (s)-[:END]->(b)
            """
            session.run(query, {"links": batch})

        for i in range(0, len(insideLinks), batch_size):
            batch = insideLinks[i:i + batch_size]

            print(i, "/", len(insideLinks), "inside links")
            query = """
            UNWIND $links AS link
            MATCH (b:Bubble {id: link.bid}), (s:Segment {id: link.sid})
            CREATE (s)-[:INSIDE]->(b)
            """
            session.run(query, {"links": batch})
    
def add_chains(chains, batch_size=10000):
    
    if len(chains) == 0: return
    with get_session() as session:

        for i in range(0, len(chains), batch_size):
            batch = chains[i:i + batch_size]

            # sb: chain.sb, pc: chain.pc
            print(i, "/", len(chains), "chains")
            query = """
            UNWIND $chains AS chain
            CREATE (:Chain {id: chain.id})
            """
            session.run(query, {"chains": batch})

        startLinks = []
        endLinks = []
        insideLinks = []
        superBubbles = []
        parentChains = []
        for chain in chains:
            start,end = chain["ends"]
            cid = chain["id"]
            startLinks.append({"sid": start, "cid": cid})
            endLinks.append({"sid": end, "cid": cid})
            superBubbles.append({"cid": cid, "bid": chain["sb"]})
            parentChains.append({"cid": cid, "bid": chain["pc"]})

            for bid in chain["bubbles"]:
                insideLinks.append({"bid": bid, "cid": cid})

        for i in range(0, len(startLinks), batch_size):
            batch = startLinks[i:i + batch_size]

            print(i, "/", len(startLinks), "start links")
            query = """
            UNWIND $links AS link
            MATCH (c:Chain {id: link.cid}), (s:Segment {id: link.sid})
            CREATE (c)-[:END]->(s)
            """
            session.run(query, {"links": batch})

        for i in range(0, len(endLinks), batch_size):
            batch = endLinks[i:i + batch_size]

            print(i, "/", len(endLinks), "end links")
            query = """
            UNWIND $links AS link
            MATCH (c:Chain {id: link.cid}), (s:Segment {id: link.sid})
            CREATE (s)-[:END]->(c)
            """
            session.run(query, {"links": batch})

        for i in range(0, len(insideLinks), batch_size):
            batch = insideLinks[i:i + batch_size]

            print(i, "/", len(insideLinks), "inside links")
            query = """
            UNWIND $links AS link
            MATCH (c:Chain {id: link.cid}), (b:Bubble {id: link.bid})
            CREATE (b)-[:INSIDE]->(c)
            """
            session.run(query, {"links": batch})

        for i in range(0, len(superBubbles), batch_size):
            batch = superBubbles[i:i + batch_size]

            print(i, "/", len(superBubbles), "superbubble links")
            query = """
            UNWIND $links AS link
            MATCH (c:Chain {id: link.cid}), (b:Bubble {id: link.bid})
            CREATE (c)-[:PARENT]->(b)
            """
            session.run(query, {"links": batch})

        for i in range(0, len(parentChains), batch_size):
            batch = parentChains[i:i + batch_size]

            print(i, "/", len(parentChains), "parent chain links")
            query = """
            UNWIND $links AS link
            MATCH (c:Chain {id: link.cid}), (pc:Chain {id: link.bid})
            CREATE (c)-[:PARENT]->(pc)
            """
            session.run(query, {"links": batch})

def connect_bubble_ends_to_chain():
    with get_session() as session:
        query = """
                MATCH (s:Segment)-[:END]-(b:Bubble)-[:INSIDE]->(c:Chain)
                WHERE NOT (c)-[:END]-(s)
                MERGE (s)-[:INSIDE]->(c)
                """
        session.run(query)


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

    with get_session() as session:

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

    with get_session() as session:

        MATCH = "MATCH (b:Bubble)-[r:INSIDE]->(c:Chain) "
        q1= MATCH + " WITH c, MIN(b.start) AS start SET c.start = start"
        q2= MATCH + " WITH c, MAX(b.end) AS end SET c.end = end"
        q3= MATCH + " WITH c, SUM(b.size) AS size SET c.size = size"
        q4= MATCH + " WITH c, SUM(b.n) AS n SET c.n = n"
        q5= MATCH + " WITH c, COLLECT(DISTINCT b.chrom)[0] AS chrom SET c.chrom = chrom"

        print("Calculating chain properties...")
        for query in [q1,q2,q3,q4,q5]:
            print(query)
            session.run(query)

    with get_session() as session:

        q6 = MATCH + " WITH c, MIN(b.x1) AS x SET c.x1 = x"
        q7 = MATCH + " WITH c, MAX(b.x2) AS x SET c.x2 = x"
        q8 = MATCH + " WITH c, MIN(b.y1) AS y SET c.y1 = y"
        q9 = MATCH + " WITH c, MAX(b.y2) AS y SET c.y2 = y"

        q10 = MATCH + """
        WITH c, SUM(b.x1*b.n) AS x1, SUM(b.x2*b.n) AS x2, SUM(2*b.n) AS n
        WITH c, (x1+x2)/n AS x
        SET c.x = x
        """
        q11 = MATCH + """
        WITH c, SUM(b.y1*b.n) AS y1, SUM(b.y2*b.n) AS y2, SUM(2*b.n) AS n
        WITH c, (y1+y2)/n AS y
        SET c.y = y
        """

        print("Calculating chain layout...")
        for query in [q6,q7,q8,q9,q10,q11]:
            print(query)
            session.run(query)

    with get_session() as session:

        MATCH = """
                MATCH (e1)-[:END]->(n)-[:END]->(e2)
                WHERE e1.start IS NOT NULL AND e2.start IS NOT NULL AND n.end is NULL 
                """

        q1 = MATCH + " SET n.chrom = e1.chrom"
        q2 = MATCH + " SET n.start = CASE WHEN e1.start < e2.start THEN e1.start ELSE e2.start END + 1"
        q3 = MATCH + " SET n.end = CASE WHEN e1.end > e2.end THEN e1.end ELSE e2.end END - 1"

        print("Calculating chain properties...")
        for query in [q1,q2,q3]:
            print(query)
            session.run(query)
            

def add_chain_complexity():
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
            

def add_segments(segments, batch_size=10000):
    if len(segments) == 0: return
    with get_session() as session:

        for i in range(0, len(segments), batch_size):
            batch = segments[i:i + batch_size]
            query = """
                UNWIND $batch AS segment
                CREATE (:Segment {
                    id: segment.id,
                    sequence: segment.seq,
                    chrom: segment.chrom,
                    start: segment.start,
                    end: segment.end,
                    x1: segment.x1,
                    y1: segment.y1,
                    y2: segment.y2,
                    x2: segment.x2,
                    length: segment.length
                })
            """
            session.run(query, {"batch": batch})

def add_relationships(links, batch_size=10000):
    if len(links) == 0: return
    with get_session() as session:

        for i in range(0, len(links), batch_size):
            batch = links[i:i + batch_size]
            query = """
            UNWIND $batch AS link
            MATCH (a:Segment {id: link.from_id}), (b:Segment {id: link.to_id})
            CREATE (a)-[:LINKS_TO {
                from_strand: link.from_strand,
                to_strand: link.to_strand,
                haplotype: link.haplotype,
                frequency: link.frequency}]->(b)
            """
            session.run(query, {"batch": batch})


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

def add_annotations(annotations, batch_size=10000):
    if len(annotations) == 0: return
    with get_session() as session:

        for i in range(0, len(annotations), batch_size):
            batch = annotations[i:i + batch_size]
            query = """
                UNWIND $batch AS ann
                CREATE (a:Annotation)
                SET a += ann
            """
            session.run(query, {"batch": batch})



