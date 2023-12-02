from db.neo4j_db import get_session

def insert_chain_nodes(session, chains, batch_size):

    for i in range(0, len(chains), batch_size):
        batch = chains[i:i + batch_size]
        # sb: chain.sb, pc: chain.pc
        print(f"{i}/{len(chains)} chains inserted.")
        query = """
                UNWIND $chains AS chain
                CREATE (:Chain {id: chain.id})
                """
        session.run(query, {"chains": batch})

def create_links(session, links, nodeType, relationship, direction):
    a = direction if direction == "<-" else "-"
    b = direction if direction == "->" else "-"
    query = """
            UNWIND $links AS link
            MATCH (n:"""+nodeType+""" {id: link.oid}), (c:Chain {id: link.cid}) 
            """ + f" CREATE (n){a}[:{relationship}]{b}(c)"
    session.run(query, {"links": links})

def insert_chain_links(session, chains, batch_size):
    startLinks,endLinks,insideLinks = [],[],[]
    superBubbles,parentChains = [],[]

    for chain in chains:
        start_id, end_id = chain["ends"]
        chain_id = chain["id"]
        startLinks.append({"cid": chain_id, "oid": start_id, })
        endLinks.append({"cid": chain_id, "oid": end_id})
        superBubbles.append({"cid": chain_id, "oid": chain["sb"]})
        parentChains.append({"cid": chain_id, "oid": chain["pc"]})

        for bubble_id in chain["bubbles"]:
            insideLinks.append({"cid": chain_id, "oid": bubble_id,})

    for i in range(0, len(startLinks), batch_size):
        batch = startLinks[i:i + batch_size]
        create_links(session, batch, "Segment", "END", "->",) #n->c

    for i in range(0, len(endLinks), batch_size):
        batch = endLinks[i:i + batch_size]
        create_links(session, batch, "Segment", "END", "<-",) #n<-c

    for i in range(0, len(insideLinks), batch_size):
        batch = insideLinks[i:i + batch_size]
        create_links(session, batch, "Bubble", "INSIDE", "->") #n->c

    for i in range(0, len(superBubbles), batch_size):
        batch = superBubbles[i:i + batch_size]
        create_links(session, batch, "Bubble", "PARENT", "<-") #n<-c

    for i in range(0, len(parentChains), batch_size):
        batch = parentChains[i:i + batch_size]
        create_links(session, batch, "Chain", "PARENT", "<-") #n<-c

def insert_chains(chains, batch_size=10000):
    if len(chains) == 0: return
    with get_session() as session:
        insert_chain_nodes(session, chains, batch_size)
        insert_chain_links(session, chains, batch_size)

def add_chain_properties():

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
                MATCH (e1:Segment)-[:END]->(c:Chain)-[:END]->(e2:Segment)
                WHERE e1.chrom IS NOT NULL AND e2.chrom IS NOT NULL AND c.chrom is NULL 
                """

        q1 = MATCH + " SET c.start = CASE WHEN e1.end < e2.end THEN e1.end + 1 ELSE e2.end + 1 END"
        q2 = MATCH + " SET c.end = CASE WHEN e1.start > e2.start THEN e1.start - 1 ELSE e2.start - 1 END"
        q3 = MATCH + " SET c.chrom = e1.chrom"


        print("Calculating chain properties...")
        for query in [q1,q2,q3]:
            print(query)
            session.run(query)
            

