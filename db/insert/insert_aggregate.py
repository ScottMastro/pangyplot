from db.neo4j_db import get_session
from collections import defaultdict
import sys

def insert_aggregate_nodes(db, session, aggregates, type, batch_size):
    total = len(aggregates)
    for i in range(0, total, batch_size):
        batch = aggregates[i:i + batch_size]

        sys.stdout.write(f"\r      Inserting {type}s: {min(i + batch_size, total)}/{total}.")
        sys.stdout.flush()

        query = f"""
            UNWIND $aggregates AS agg
            CREATE (:{type} {{
                db: $db,
                id: agg.id,
                subtype: agg.subtype,
                nesting_level: agg.nesting_level,
                depth: agg.depth
            }})
        """
        #        inside: agg.inside,
        #        pc: agg.pc,
        #        sb: agg.sb

        session.run(query, {"aggregates": batch, "db": db})

    print(f"\r      Inserting {type}s: {total}/{total}.")

def insert_aggregate_links(db, session, bubbles, chains, batch_size):
    linkmap = defaultdict(list)

    def insert_link(db, session, links, label_a, label_b, rel):
        query = f"""
            UNWIND $links AS link
            MATCH (a:{label_a} {{db: $db, id: link.id_a}}), (b:{label_b} {{db: $db, id: link.id_b}})
            CREATE (a)-[:{rel}]->(b)
        """
        session.run(query, {"links": links, "db": db})

    for bubble in bubbles:
        bid = bubble["id"]
        start_id, end_id = bubble["ends"]

        linkmap["Segment.END.Bubble"].append({"id_a": start_id, "id_b": bid})
        linkmap["Bubble.END.Segment"].append({"id_a": bid, "id_b": end_id})

        if bubble["sb"]:
            linkmap["Bubble.INSIDE.Bubble"].append({"id_a": bid, "id_b": bubble["sb"]})
        for sid in bubble["inside"]:
            linkmap["Segment.INSIDE.Bubble"].append({"id_a": sid, "id_b": bid})

    for chain in chains:
        cid = chain["id"]
        start_id, end_id = chain["ends"]

        linkmap["Segment.CHAIN_END.Chain"].append({"id_a": start_id, "id_b": cid})
        linkmap["Chain.CHAIN_END.Segment"].append({"id_a": cid, "id_b": end_id})

        if chain["sb"]:
            linkmap["Chain.PARENT_SB.Bubble"].append({"id_a": cid, "id_b": chain["sb"]})
        for bid_inside in chain["inside"]:
            linkmap["Bubble.CHAINED.Chain"].append({"id_a": bid_inside, "id_b": cid})

    for key, batch in linkmap.items():
        if not batch: continue
        label_a, rel, label_b = key.split('.')
        for i in range(0, len(batch), batch_size):
            insert_link(db, session, batch[i:i + batch_size], label_a, label_b, rel)

def add_aggregate_properties(max_depth):
    with get_session() as (db, session):
        
        queries = [
            "WITH a, MIN(n.start) AS start SET a.start = start",
            "WITH a, MAX(n.end) AS end SET a.end = end",
            "WITH a, SUM(n.length) AS length SET a.length = length",
            "WITH a, MAX(n.length) AS largest SET a.largest_child = largest",
            "WITH a, COUNT(*) AS children SET a.children = children",
            "WITH a, COLLECT(DISTINCT n.genome)[0] AS genome SET a.genome = genome",
            "WITH a, COLLECT(DISTINCT n.chrom)[0] AS chrom SET a.chrom = chrom",
            "WITH a, ANY(x IN COLLECT(n.is_ref) WHERE x = true) AS has_ref SET a.is_ref = has_ref",
            "WITH a, SUM(n.gc_count) AS count SET a.gc_count = count",
        ]

        print("      Calculating aggregate properties...")

        match_bubble = f"MATCH (n)-[:INSIDE]->(a:Bubble) WHERE a.db = $db AND a.depth = $depth"
        match_chain = f"MATCH (n)-[:CHAINED]->(a:Chain) WHERE a.db = $db AND a.depth = $depth"

        for d in range(max_depth + 1):
            print("depth", d)
            for query in queries:
                session.run(f"{match_bubble} {query}", {"db": db, "depth": d})
                session.run(f"{match_chain} {query}", {"db": db, "depth": d})


        input()

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
            session.run(query, {"db": db})

def insert_bubbles_and_chains(bubbles, chains, batch_size=10000):
    if len(bubbles) == 0: return
    with get_session() as (db, session):
        insert_aggregate_nodes(db, session, bubbles, "Bubble", batch_size)
        insert_aggregate_nodes(db, session, chains, "Chain", batch_size)
        insert_aggregate_links(db, session, bubbles, chains, batch_size)

        max_depth = max([x["depth"] for x in chains + bubbles])

        add_aggregate_properties(max_depth)
