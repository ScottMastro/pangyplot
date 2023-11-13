from neo4j import GraphDatabase,exceptions

uri = "neo4j://localhost:7687"
username = "neo4j"
password = "password"  # Replace with the password you set

def add_segments(segments, batch_size=10000):
    if len(segments) == 0: return
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:

        for i in range(0, len(segments), batch_size):
            batch = segments[i:i + batch_size]
            query = "UNWIND $batch AS segment CREATE (:Segment {id: segment.id, sequence: segment.seq})"
            session.run(query, {"batch": batch})

        #for segment in segments:
        #    session.run("CREATE (:Segment {id: $id, sequence: $sequence})", id=segment["id"], sequence=segment["seq"])
    
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
            CREATE (a)-[:LINKS_TO {from_strand: link.from_strand, to_strand: link.to_strand}]->(b)
            """
            session.run(query, {"batch": batch})

    driver.close()

def add_paths(paths, batch_size=10000):
    if len(paths) == 0: return
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:
        for path in paths:
            for i in range(0, len(path["path"]), batch_size):
                batch = []
                for j in range(i-1):
                    link = {"from_id": path["path"][i+j],
                            "to_id": path["path"][i+j+1],
                            "from_strand": path["strand"][i+j],
                            "to_strand": path["strand"][i+j+1],
                            "position": path["position"][i+j],
                            "sample": path["sample"],
                            "hap": path["hap"]
                             }      
                    batch.append(link)          
                print(i, "/", len(path["path"]))
                query = """
                UNWIND $batch AS link
                MATCH (a:Segment {id: link.from_id}), (b:Segment {id: link.to_id})
                CREATE (a)-[:HAPLOTYPE {from_strand: link.from_strand, to_strand: link.to_strand, position: link.position, sample: link.sample, hap : link.hap }]->(b)
                """
                session.run(query, {"batch": batch})

    driver.close()

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
            deleted = session.write_transaction(delete_in_batches, batch_size=500000)
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
    driver.close()