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
            for query in queries:
                session.run(f"{match_bubble} {query}", {"db": db, "depth": d})
                session.run(f"{match_chain} {query}", {"db": db, "depth": d})

        match_bubble = "MATCH (n)-[:INSIDE]->(a:Bubble)"
        match_chain = "MATCH (n)-[:CHAINED]->(a:Chain)"

        query = """
                WHERE a.db = $db AND a.depth = $depth

                WITH a,
                    avg(n.x1) AS avgX1,
                    avg(n.x2) AS avgX2,
                    min(n.x1) AS minX1,
                    max(n.x1) AS maxX1,
                    min(n.x2) AS minX2,
                    max(n.x2) AS maxX2,
                    avg(n.y1) AS avgY1,
                    avg(n.y2) AS avgY2,
                    min(n.y1) AS minY1,
                    max(n.y1) AS maxY1,
                    min(n.y2) AS minY2,
                    max(n.y2) AS maxY2

                SET a.x1 = CASE WHEN avgX1 < avgX2 THEN minX1 ELSE maxX1 END,
                    a.x2 = CASE WHEN avgX1 < avgX2 THEN maxX2 ELSE minX2 END,
                    a.y1 = CASE WHEN avgY1 < avgY2 THEN minY1 ELSE maxY1 END,
                    a.y2 = CASE WHEN avgY1 < avgY2 THEN maxY2 ELSE minY2 END                
                """
        
        for d in range(max_depth + 1):
            session.run(f"{match_bubble} {query}", {"db": db, "depth": d})
            session.run(f"{match_chain} {query}", {"db": db, "depth": d})

def adjust_compacted_nodes(db, session):

        query = """
                MATCH (b:Bubble)-[r:END]-(e:Segment)<-[:COMPACT]-(c:Segment)-[:LINKS_TO]-(s:Segment)-[:INSIDE]->(b)
                WHERE b.db = $db AND c <> e
                WITH DISTINCT b, r, c, startNode(r) AS from, endNode(r) AS to
                DELETE r
                FOREACH (_ IN CASE WHEN from = b THEN [1] ELSE [] END |
                    CREATE (b)-[:END]->(c)
                )
                FOREACH (_ IN CASE WHEN to = b THEN [1] ELSE [] END |
                    CREATE (c)-[:END]->(b)
                )
                """
        session.run(query, {"db": db})

        #TODO:
        #query = """
        #        MATCH (a:Chain)-[r:END]-(e:Segment)<-[:COMPACT]-(c:Segment)-[:CHAINED]-(s:Segment)-[:INSIDE]->(b)
        #        WHERE a.db = $db AND c <> e
        #        WITH DISTINCT b, r, c, startNode(r) AS from, endNode(r) AS to
        #        DELETE r
        #        FOREACH (_ IN CASE WHEN from = b THEN [1] ELSE [] END |
        #            CREATE (a)-[:CHAIN_END]->(c)
        #        )
        #        FOREACH (_ IN CASE WHEN to = b THEN [1] ELSE [] END |
        #            CREATE (c)-[:CHAIN_END]->(a)
        #        )
        #        """
        #session.run(query, {"db": db})


def insert_bubbles_and_chains(bubbles, chains, batch_size=10000):
    if len(bubbles) == 0: return
    with get_session() as (db, session):
        insert_aggregate_nodes(db, session, bubbles, "Bubble", batch_size)
        insert_aggregate_nodes(db, session, chains, "Chain", batch_size)
        insert_aggregate_links(db, session, bubbles, chains, batch_size)
        
        adjust_compacted_nodes(db, session)

        max_depth = max([x["depth"] for x in chains + bubbles])

        add_aggregate_properties(max_depth)
