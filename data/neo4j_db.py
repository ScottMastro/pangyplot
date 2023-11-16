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
            MATCH (a:Bubble {id: link.bid}), (b:Segment {id: link.sid})
            CREATE (a)-[:BUBBLE_END]->(b)
            """
            session.run(query, {"links": batch})

        for i in range(0, len(insideLinks), batch_size):
            batch = insideLinks[i:i + batch_size]

            print(i, "/", len(insideLinks), "inside links")
            query = """
            UNWIND $links AS link
            MATCH (a:Bubble {id: link.bid}), (b:Segment {id: link.sid})
            CREATE (a)-[:BUBBLE_INSIDE]->(b)
            """
            session.run(query, {"links": batch})

    driver.close()
    
def add_chains(chains, batch_size=10000):
    
    if len(chains) == 0: return
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:

        for i in range(0, len(chains), batch_size):
            batch = chains[i:i + batch_size]

            print(i, "/", len(chains), "chains")
            query = """
            UNWIND $chains AS chain
            CREATE (:Chain {id: chain.id, sb: chain.sb, pc: chain.pc})
            """
            session.run(query, {"chains": batch})

        endLinks = []
        insideLinks = []
        for chain in chains:
            start,end = chain["ends"]
            cid = chain["id"]
            endLinks.append({"sid": start, "cid": cid})
            endLinks.append({"sid": end, "cid": cid})

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
            MATCH (a:Chain {id: link.cid}), (b:Bubble {id: link.bid})
            CREATE (a)-[:CHAIN_INSIDE]->(b)
            """
            session.run(query, {"links": batch})

    driver.close()

#def create_segment_index():
#    driver = GraphDatabase.driver(uri, auth=(username, password))
#    with driver.session() as session:
#        session.run("CREATE INDEX FOR (n:Segment) ON (n.id)")
#    driver.close()

def add_segments(segments, batch_size=10000):
    if len(segments) == 0: return
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:

        for i in range(0, len(segments), batch_size):
            batch = segments[i:i + batch_size]
            query = "UNWIND $batch AS segment CREATE (:Segment {id: segment.id, x1: segment.x1, y1: segment.y1, y2: segment.y2, x2: segment.x2, sequence: segment.seq, length: segment.length})"
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
            CREATE (a)-[:LINKS_TO {from_strand: link.from_strand, to_strand: link.to_strand, haplotype: link.haplotype, frequency: link.frequency}]->(b)
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

def db_init():
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:
        try:
            session.run("CREATE CONSTRAINT FOR (segment:Segment) REQUIRE segment.id IS UNIQUE")
        except exceptions.ClientError as e:
            if "EquivalentSchemaRuleAlreadyExists" in e.code:
                #print("Constraint already exists.")
                pass
            else:
                raise

        try:
            session.run("CREATE CONSTRAINT FOR (bubble:Bubble) REQUIRE bubble.id IS UNIQUE")
        except exceptions.ClientError as e:
            if "EquivalentSchemaRuleAlreadyExists" in e.code:
                #print("Constraint already exists.")
                pass
            else:
                raise

        try:
            session.run("CREATE CONSTRAINT FOR (chain:Chain) REQUIRE chain.id IS UNIQUE")
        except exceptions.ClientError as e:
            if "EquivalentSchemaRuleAlreadyExists" in e.code:
                #print("Constraint already exists.")
                pass
            else:
                raise
    driver.close()