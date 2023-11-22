from neo4j import GraphDatabase,exceptions
import time

uri = "neo4j://localhost:7687"
username = "neo4j"
password = "password"  # Replace with the password you set


def add_bubbles(bubbles, batch_size=10000):
    
    if len(bubbles) == 0: return
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:

        for i in range(0, len(bubbles), batch_size):
            batch = bubbles[i:i + batch_size]

            print(i, "/", len(bubbles), "bubbles")
            query = """
            UNWIND $bubbles AS bubble
            CREATE (:Bubble {id: bubble.id, type: bubble.type})
            """
            session.run(query, {"bubbles": batch})

        endLinks = []
        insideLinks = []
        for bubble in bubbles:
            start,end = bubble["ends"]
            bid = bubble["id"]
            endLinks.append({"sid": start, "bid": bid})
            endLinks.append({"sid": end, "bid": bid})

            for sid in bubble["inside"]:
                insideLinks.append({"sid": sid, "bid": bid})

        for i in range(0, len(endLinks), batch_size):
            batch = endLinks[i:i + batch_size]

            print(i, "/", len(endLinks), "end links")
            query = """
            UNWIND $links AS link
            MATCH (b:Bubble {id: link.bid}), (s:Segment {id: link.sid})
            CREATE (b)-[:END]->(s)
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

    driver.close()
    
def add_chains(chains, batch_size=10000):
    
    if len(chains) == 0: return
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:

        for i in range(0, len(chains), batch_size):
            batch = chains[i:i + batch_size]

            # sb: chain.sb, pc: chain.pc
            print(i, "/", len(chains), "chains")
            query = """
            UNWIND $chains AS chain
            CREATE (:Chain {id: chain.id})
            """
            session.run(query, {"chains": batch})

        endLinks = []
        insideLinks = []
        superBubbles = []
        parentChains = []
        for chain in chains:
            start,end = chain["ends"]
            cid = chain["id"]
            endLinks.append({"sid": start, "cid": cid})
            endLinks.append({"sid": end, "cid": cid})
            superBubbles.append({"cid": cid, "bid": chain["sb"]})
            parentChains.append({"cid": cid, "bid": chain["pc"]})

            for bid in chain["bubbles"]:
                insideLinks.append({"bid": bid, "cid": cid})

        for i in range(0, len(endLinks), batch_size):
            batch = endLinks[i:i + batch_size]

            print(i, "/", len(endLinks), "end links")
            query = """
            UNWIND $links AS link
            MATCH (a:Chain {id: link.cid}), (b:Segment {id: link.sid})
            CREATE (a)-[:END]->(b)
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

    driver.close()

def connect_bubble_ends_to_chain():
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:
        query = """
                MATCH (s:Segment)<-[:END]-(b:Bubble)-[:INSIDE]->(c:Chain)
                WHERE NOT (c)-[:END]->(s)
                MERGE (s)-[:INSIDE]->(c)
                """
        session.run(query)
    driver.close()


def add_bubble_properties():
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:
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

    driver.close()


def add_segments(segments, batch_size=10000):
    if len(segments) == 0: return
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:

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

    driver.close()

def add_relationships(links, batch_size=10000):
    if len(links) == 0: return
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:

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

    driver.close()

'''
def add_paths(paths, batch_size=10000):
    if len(paths) == 0: return
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:
        for path in paths:
            path_info = {"sample": path["sample"], "hap": path["hap"]}
            links = []

            start_time = time.time()
            
            for i,from_id in enumerate(path["path"][:-1]):
                link = {"from_id": from_id,
                        "to_id": path["path"][i+1],
                        "from_strand": path["strand"][i],
                        "to_strand": path["strand"][i+1],
                        "position": path["position"][i]}
                links.append(link)

            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"The links took {elapsed_time} seconds to run.")

            for i in range(0, len(links), batch_size):

                start_time = time.time()

                batch = links[i:i + batch_size]

                print(i, "/", len(path["path"]))
                query = """
                UNWIND $batch AS link
                MATCH (a:Segment {id: link.from_id}), (b:Segment {id: link.to_id})
                CREATE (a)-[:HAPLOTYPE {from_strand: link.from_strand, to_strand: link.to_strand, position: link.position, sample: $path.sample, hap : $path.hap }]->(b)
                """
                session.run(query, {"batch": batch, "path": path_info})

                end_time = time.time()
                elapsed_time = end_time - start_time
                print(f"The insert took {elapsed_time} seconds to run, {round((batch_size/1000)/elapsed_time, 2)}k per second.")


    driver.close()
    
def add_haplotypes(collapseDict, sampleIdDict, batch_size=10000):
    
    if len(collapseDict) == 0: return
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:
        links = []
        for key in collapseDict:
            from_key, to_key = key
            link = {"from_id": from_key[:-1],
                    "to_id": to_key[:-1],
                    "from_strand": from_key[-1],
                    "to_strand": to_key[-1],
                    "haplotypes": collapseDict[key]}
            #print(link)
            links.append(link)

        for i in range(0, len(links), batch_size):
            batch = links[i:i + batch_size]

            print(i, "/", len(links))
            query = """
            UNWIND $links AS link
            MATCH (a:Segment {id: link.from_id})-[r:LINKS_TO]->(b:Segment {id: link.to_id})
            WHERE r.to_strand = link.to_strand AND r.from_strand = link.from_strand 
            SET r.haplotypes = link.haplotypes
            """
            session.run(query, {"links": batch})

    driver.close()
    '''


def drop_all():

    driver = GraphDatabase.driver(uri, auth=(username, password))

    def delete_in_batches(tx, batch_size):
        query = (
            "MATCH (n) "
            "WITH n LIMIT $batchSize "
            "DETACH DELETE n "
            "RETURN count(n) as deletedCount"
        )
        result = tx.run(query, batchSize=batch_size)
        return result.single()[0]

    with driver.session() as session:
        total_deleted = 0
        while True:
            deleted = session.write_transaction(delete_in_batches, batch_size=10000)
            if deleted == 0:
                break
            total_deleted += deleted
            print(f"Deleted {total_deleted} nodes so far...")
        print("Deletion complete.")
    driver.close()

def drop_bubbles():
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:

        def delete_bubbles(tx, batch_size):
            query = (
                "MATCH (n:Bubble) "
                "WITH n LIMIT $batchSize "
                "DETACH DELETE n "
                "RETURN count(n) as deletedCount"
            )
            result = tx.run(query, batchSize=batch_size)
            return result.single()[0]

        total_deleted = 0
        while True:
            deleted = session.write_transaction(delete_bubbles, batch_size=10000)
            if deleted == 0:
                break
            total_deleted += deleted
            print(f"Deleted {total_deleted} bubbles so far...")

        def delete_chains(tx, batch_size):
            query = (
                "MATCH (n:Chain) "
                "WITH n LIMIT $batchSize "
                "DETACH DELETE n "
                "RETURN count(n) as deletedCount"
            )
            result = tx.run(query, batchSize=batch_size)
            return result.single()[0]

        total_deleted = 0
        while True:
            deleted = session.write_transaction(delete_chains, batch_size=10000)
            if deleted == 0:
                break
            total_deleted += deleted
            print(f"Deleted {total_deleted} bubbles so far...")

        print("Deletion complete.")
    driver.close()

def create_segment_index(session, type, property):
    try:
        session.run(f"CREATE INDEX FOR (n:{type}) ON (n.{property})")
    except exceptions.ClientError as e:
        if "EquivalentSchemaRuleAlreadyExists" in e.code:
            #print("Index already exists.")
            pass
        else:
            raise

def create_restraint(session, type, property):
    try:
        session.run(f"CREATE CONSTRAINT FOR (n:{type}) REQUIRE n.{property} IS UNIQUE")
    except exceptions.ClientError as e:
        if "EquivalentSchemaRuleAlreadyExists" in e.code:
            #print("Constraint already exists.")
            pass
        else:
            raise

def db_init():
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:

        create_restraint(session, "Segment", "id")
        create_segment_index(session, "Segment", "chrom")
        create_segment_index(session, "Segment", "start")
        create_segment_index(session, "Segment", "end")

        create_restraint(session, "Bubble", "id")
        create_segment_index(session, "Bubble", "chrom")
        create_segment_index(session, "Bubble", "start")
        create_segment_index(session, "Bubble", "end")

        create_restraint(session, "Chain", "id")
        create_segment_index(session, "Chain", "chrom")
        create_segment_index(session, "Chain", "start")
        create_segment_index(session, "Chain", "end")

    driver.close()