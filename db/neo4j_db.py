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
            CREATE (b)-[:BUBBLE_END]->(s)
            """
            session.run(query, {"links": batch})

        for i in range(0, len(insideLinks), batch_size):
            batch = insideLinks[i:i + batch_size]

            print(i, "/", len(insideLinks), "inside links")
            query = """
            UNWIND $links AS link
            MATCH (b:Bubble {id: link.bid}), (s:Segment {id: link.sid})
            CREATE (s)-[:BUBBLE_INSIDE]->(b)
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
            CREATE (a)-[:CHAIN_END]->(b)
            """
            session.run(query, {"links": batch})

        for i in range(0, len(insideLinks), batch_size):
            batch = insideLinks[i:i + batch_size]

            print(i, "/", len(insideLinks), "inside links")
            query = """
            UNWIND $links AS link
            MATCH (c:Chain {id: link.cid}), (b:Bubble {id: link.bid})
            CREATE (b)-[:CHAIN_INSIDE]->(c)
            """
            session.run(query, {"links": batch})

        for i in range(0, len(superBubbles), batch_size):
            batch = superBubbles[i:i + batch_size]

            print(i, "/", len(superBubbles), "superbubble links")
            query = """
            UNWIND $links AS link
            MATCH (c:Chain {id: link.cid}), (b:Bubble {id: link.bid})
            CREATE (c)-[:CHAIN_SUPERBUBBLE]->(b)
            """
            session.run(query, {"links": batch})

        for i in range(0, len(parentChains), batch_size):
            batch = parentChains[i:i + batch_size]

            print(i, "/", len(parentChains), "parent chain links")
            query = """
            UNWIND $links AS link
            MATCH (c:Chain {id: link.cid}), (pc:Chain {id: link.bid})
            CREATE (c)-[:PARENT_CHAIN]->(pc)
            """
            session.run(query, {"links": batch})

    driver.close()

def add_bubble_properties():
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:
        query = """
        MATCH (b:Bubble)
        MATCH (s:Segment)-[r:BUBBLE_INSIDE]->(b)
        WITH b, 
            MIN(s.pos) AS minPos, 
            MAX(s.pos + s.length - 1) AS maxPos,
            SUM(s.length) AS totalLength,
            SUM(1) AS n,
            COLLECT(DISTINCT s.chrom)[0] AS chrom
            SET b.minPosition = minPos, 
            b.maxPosition = maxPos,
            b.chrom = chrom,
            b.size = totalLength,
            b.n = n
        """
        print("Calculating bubble sizes...")
        session.run(query)

        print("Calculating bubble layout...")

        query = """
        MATCH (b:Bubble)
        MATCH (s:Segment)-[r:BUBBLE_INSIDE]->(b)
        WITH b, 
            MIN(s.x1) AS minX1, MAX(s.x1) AS maxX1, 
            MIN(s.x2) AS minX2, MAX(s.x2) AS maxX2
        WITH b, 
            CASE WHEN minX1 < minX2 THEN minX1 ELSE minX2 END AS minX,
            CASE WHEN maxX1 > maxX2 THEN maxX1 ELSE maxX2 END AS maxX
        SET b.x1 = minX, b.x2 = maxX
        """
        session.run(query)
        
        query = """
        MATCH (s:Segment)-[r:BUBBLE_INSIDE]->(b:Bubble)
        WITH b, MIN(s.y1) AS minY1, MIN(s.y2) AS minY2
        WITH b, CASE WHEN minY1 < minY2 THEN minY1 ELSE minY2 END AS minY
        SET b.y1 = minY
        """
        session.run(query)

        query = """
        MATCH (s:Segment)-[r:BUBBLE_INSIDE]->(b:Bubble)
        WITH b, MAX(s.y1) AS maxY1, MAX(s.y2) AS maxY2
        WITH b, CASE WHEN maxY1 < maxY2 THEN maxY2 ELSE maxY1 END AS maxY
        SET b.y2 = maxY
        """
        session.run(query)


        query = """
        MATCH (s:Segment)-[r:BUBBLE_INSIDE]->(b:Bubble)
        WITH b,
            SUM(s.y1) AS y1,
            SUM(s.y2) AS y2,
            SUM(2) AS n
        WITH b, 
            (y1+y2)/n AS y
        SET b.y = y
        """
        session.run(query)

        query = """
        MATCH (s:Segment)-[r:BUBBLE_INSIDE]->(b:Bubble)
        WITH b,
            SUM(s.x1) AS x1, 
            SUM(s.x2) AS x2,
            SUM(2) AS n
        WITH b, 
            (x1+x2)/n AS x
        SET b.x = x
        """
        session.run(query)

        query = """
        MATCH (b:Bubble)-[r:CHAIN_INSIDE]->(c:Chain)
        WITH c, 
            MIN(b.minPosition) AS minPos,
            MAX(b.maxPosition) AS maxPos,
            SUM(b.size) AS totalLength,
            SUM(b.n) AS n,
            COLLECT(DISTINCT b.chrom)[0] AS chrom
        SET c.minPosition = minPos,
            c.maxPosition = maxPos,
            c.size = totalLength, 
            c.chrom = chrom, 
            c.n = n
        """
        print("Calculating chain sizes...")
        session.run(query)

        print("Calculating chain layout...")

        query = """
        MATCH (b:Bubble)-[r:CHAIN_INSIDE]->(c:Chain)
        WITH c, 
            MIN(b.x1) AS minX, 
            MAX(b.x2) AS maxX, 
            MIN(b.y1) AS minY, 
            MAX(b.y2) AS maxY
        SET c.x1 = minX, c.x2 = maxX, c.y1 = minY, c.y2 = maxY
        """
        session.run(query)

        query = """
        MATCH (b:Bubble)-[r:CHAIN_INSIDE]->(c:Chain)
        WITH c,
            SUM(b.x1*b.n) AS x1, 
            SUM(b.x2*b.n) AS x2,
            SUM(b.y1*b.n) AS y1,
            SUM(b.y2*b.n) AS y2,
            SUM(2*b.n) AS n
        WITH c, 
            (x1+x2)/n AS x, (y1+y2)/n AS y
        SET c.x = x, c.y = y
        """
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
                    pos: segment.pos,
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
        create_segment_index(session, "Segment", "pos")

        create_restraint(session, "Bubble", "id")
        create_restraint(session, "Chain", "id")

    driver.close()