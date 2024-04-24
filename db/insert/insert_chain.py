from db.neo4j_db import get_session

def insert_chain_nodes(db, session, chains, batch_size):

    for i in range(0, len(chains), batch_size):
        batch = chains[i:i + batch_size]
        # sb: chain.sb, pc: chain.pc
        print(f"{i}/{len(chains)} chains inserted.")
        query = """
                UNWIND $chains AS chain
                CREATE (:Chain {db: $db, id: chain.id})
                """
        session.run(query, {"chains": batch, "db": db})

def create_links(db, session, links, nodeType, relationship, direction):
    a = direction if direction == "<-" else "-"
    b = direction if direction == "->" else "-"
    query = """
            UNWIND $links AS link
            MATCH (n:"""+nodeType+""" {db: $db, id: link.oid}), (c:Chain {db: $db, id: link.cid})
            """ + f" CREATE (n){a}[:{relationship}]{b}(c)"
    session.run(query, {"links": links, "db": db})

def insert_chain_links(db, session, chains, batch_size):
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
        create_links(db, session, batch, "Segment", "END", "->",) #n->c

    for i in range(0, len(endLinks), batch_size):
        batch = endLinks[i:i + batch_size]
        create_links(db, session, batch, "Segment", "END", "<-",) #n<-c

    for i in range(0, len(insideLinks), batch_size):
        batch = insideLinks[i:i + batch_size]
        create_links(db, session, batch, "Bubble", "INSIDE", "->") #n->c

    for i in range(0, len(superBubbles), batch_size):
        batch = superBubbles[i:i + batch_size]
        create_links(db, session, batch, "Bubble", "INSIDE", "<-") #n<-c

    for i in range(0, len(parentChains), batch_size):
        batch = parentChains[i:i + batch_size]
        create_links(db, session, batch, "Chain", "INSIDE", "<-") #n<-c

def insert_chains(chains, batch_size=10000):
    if len(chains) == 0: return
    with get_session() as (db, session):
        insert_chain_nodes(db, session, chains, batch_size)
        insert_chain_links(db, session, chains, batch_size)

def add_chain_properties():

    with get_session() as (db, session):

        MATCH = "MATCH (b:Bubble)-[r:INSIDE]->(c:Chain) WHERE c.db = $db "
        q1= MATCH + " WITH c, MIN(b.start) AS start SET c.start = start"
        q2= MATCH + " WITH c, MAX(b.end) AS end SET c.end = end"
        q3= MATCH + " WITH c, SUM(b.size) AS size SET c.size = size"
        q4= MATCH + " WITH c, MAX(b.size) AS largest SET c.largest_child = largest"
        q5= MATCH + " WITH c, SUM(b.n) AS n SET c.n = n"
        q6= MATCH + " WITH c, COLLECT(DISTINCT b.chrom)[0] AS chrom SET c.chrom = chrom"
        q7= MATCH + " WITH c, COLLECT(DISTINCT b.genome)[0] AS genome SET c.genome = genome"

        #todo remove?
        #q7 = MATCH + """
        #WITH c, SUM(b.x1*b.n) AS x1, SUM(b.x2*b.n) AS x2, SUM(2*b.n) AS n
        #WITH c, (x1+x2)/n AS x
        #SET c.x = x
        #"""
        #todo remove?
        #q8 = MATCH + """
        #WITH c, SUM(b.y1*b.n) AS y1, SUM(b.y2*b.n) AS y2, SUM(2*b.n) AS n
        #WITH c, (y1+y2)/n AS y
        #SET c.y = y
        #"""

        print("Calculating chain properties...")
        for query in [q1,q2,q3,q4,q5,q6,q7]:
            print(query)
            session.run(query, {"db": db})

    with get_session() as (db, session):

        MATCH = """
            MATCH (x)-[:INSIDE]->(c:Chain)<-[r:END]-(s:Segment)
            WHERE c.db = $db AND exists((x)-[]-(s))
        """

        q9 = MATCH + " WITH c, avg(x.x1) AS avgX1 SET c.x1 = avgX1"
        q10 = MATCH + " WITH c, avg(x.y1) AS avgY1 SET c.y1 = avgY1"

        MATCH = """
            MATCH (x)-[:INSIDE]->(c:Chain)-[r:END]->(s:Segment)
            WHERE c.db = $db AND exists((x)-[]-(s))
        """

        q11 = MATCH + " WITH c, avg(x.x2) AS avgX2 SET c.x2 = avgX2"
        q12 = MATCH + " WITH c, avg(x.y2) AS avgY2 SET c.y2 = avgY2"


        print("Calculating chain layout...")
        for query in [q9,q10,q11,q12]:
            print(query)
            session.run(query, {"db": db})

        #q10 = MATCH + " WITH c, MAX(b.x2) AS x SET c.x2 = x"
        #q11 = MATCH + " WITH c, MIN(b.y1) AS y SET c.y1 = y"
        #q12 = MATCH + " WITH c, MAX(b.y2) AS y SET c.y2 = y"


    with get_session() as (db, session):

        MATCH = """
                MATCH (e1:Segment)-[:END]->(c:Chain)-[:END]->(e2:Segment)
                WHERE e1.db = $db AND e2.db = $db""" + \
                " AND e1.genome = e2.genome" + \
                " AND e1.chrom IS NOT NULL AND e2.chrom IS NOT NULL AND c.chrom is NULL"

        q1 = MATCH + " SET c.start = CASE WHEN e1.end < e2.end THEN e1.end + 1 ELSE e2.end + 1 END"
        q2 = MATCH + " SET c.end = CASE WHEN e1.start > e2.start THEN e1.start - 1 ELSE e2.start - 1 END"
        q3 = MATCH + " SET c.genome = e1.genome"
        q4 = MATCH + " SET c.chrom = e1.chrom"


        print("Calculating chain properties...")
        for query in [q1,q2,q3,q4]:
            print(query)
            session.run(query, {"db": db})
            

