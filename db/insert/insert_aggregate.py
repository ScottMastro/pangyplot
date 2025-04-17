from db.neo4j_db import get_session
from collections import defaultdict
import sys

import db.modify.preprocess_modifications as modify

def insert_aggregate_nodes(aggregates, type, batch_size):
    total = len(aggregates)
    
    with get_session(collection=True) as (db, collection, session):

        for i in range(0, total, batch_size):
            batch = aggregates[i:i + batch_size]

            sys.stdout.write(f"\r      Inserting {type}s: {min(i + batch_size, total)}/{total}.")

            query = f"""
                UNWIND $aggregates AS agg
                CREATE (:{type} {{
                    db: $db,
                    collection: $col,
                    id: toString(agg.id),
                    subtype: agg.subtype,
                    nesting_level: agg.nesting_level,
                    depth: agg.depth
                }})
            """
            session.run(query, {"aggregates": batch, "col": collection, "db": db})

        print(f"\r      Inserting {type}s: {total}/{total}.")

def insert_aggregate_links(bubbles, chains, batch_size):
    linkmap = defaultdict(list)

    with get_session(collection=True) as (db, collection, session):

        def insert_link(links, label_a, label_b, rel):
            query = f"""
                UNWIND $links AS link
                MATCH (a:{label_a} {{db: $db, collection: $col, id: toString(link.id_a)}}),
                    (b:{label_b} {{db: $db, collection: $col, id: toString(link.id_b)}})
                CREATE (a)-[:{rel}]->(b)
            """
            session.run(query, {"links": links, "col": collection,  "db": db})

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
                insert_link(batch[i:i + batch_size], label_a, label_b, rel)


def add_child_information(max_depth):
    with get_session(collection=True) as (db, collection, session):
        
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


        match_bubble = f"MATCH (n)-[:INSIDE]->(a:Bubble) WHERE a.db = $db AND a.collection = $col AND a.depth = $depth"
        match_chain = f"MATCH (n)-[:CHAINED]->(a:Chain) WHERE a.db = $db AND a.collection = $col AND a.depth = $depth"

        for d in range(max_depth + 1):
            for query in queries:
                params = {"db": db, "col": collection, "depth": d}
                session.run(f"{match_bubble} {query}", params)
                session.run(f"{match_chain} {query}", params)

def add_position_information(max_depth):
    with get_session(collection=True) as (db, collection, session):

        match_bubble = "MATCH (n)-[:INSIDE]->(a:Bubble)"
        match_chain = "MATCH (n)-[:CHAINED]->(a:Chain)"

        query = """
                WHERE a.db = $db AND a.collection = $col AND a.depth = $depth

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
            params = {"db": db, "col": collection, "depth": d}

            session.run(f"{match_bubble} {query}", params)
            session.run(f"{match_chain} {query}", params)

def add_haplotype_information(max_depth):
    with get_session(collection=True) as (db, collection, session):

        hap_query_bubble = """
            MATCH (s:Segment)-[l:LINKS_TO]-(s2), 
                  (s)-[:INSIDE]->(a:Bubble)
            WHERE a.db = $db AND a.collection = $col 
              AND a.depth = $depth 
              AND l.haplotype IS NOT NULL
            RETURN ID(a) AS aid, l.haplotype AS hap

            UNION ALL

            MATCH (n)-[e:END]-(b:Bubble)-[:INSIDE]->(a:Bubble)
            WHERE a.db = $db AND a.collection = $col 
              AND a.depth = $depth 
              AND e.haplotype IS NOT NULL
            RETURN ID(a) AS aid, e.haplotype AS hap
        """

        hap_write_bubble = """
            UNWIND $batch AS item
            MATCH (a) WHERE ID(a) = item.id
            MATCH (s:Segment)-[e:END]-(a)
            SET e.haplotype = item.hap
        """

        hap_query_chain = """
            MATCH (n)-[e:END]-(b:Bubble)-[:CHAINED]->(a:Chain)
            WHERE a.db = $db AND a.collection = $col 
              AND a.depth = $depth 
              AND e.haplotype IS NOT NULL
            RETURN ID(a) AS aid, e.haplotype AS hap
        """

        hap_write_chain = """
            UNWIND $batch AS item
            MATCH (a) WHERE ID(a) = item.id
            MATCH (s:Segment)-[e:CHAIN_END]-(a)
            SET e.haplotype = item.hap
        """

        def update_hap(search_query, update_query, batch_size=1000):
            for d in range(max_depth + 1):
                params = {"db": db, "col": collection, "depth": d}
                result = session.run(search_query, params)

                hap_map = defaultdict(int)

                for record in result:
                    aid = record["aid"]
                    hap_hex = record["hap"]
                    hap_map[aid] |= int(hap_hex, 16)

                update_batch = []
                for aid in hap_map:
                    hmap = {"id": aid, "hap": hex(hap_map[aid])[2:]}
                    update_batch.append(hmap)
                
                for i in range(0, len(update_batch), batch_size):
                    batch = update_batch[i:i + batch_size]
                    session.run(update_query, {"batch": batch})


        update_hap(hap_query_bubble, hap_write_bubble, batch_size=1000)
        update_hap(hap_query_chain, hap_write_chain, batch_size=1000)


def insert_bubbles_and_chains(bubbles, chains, batch_size=10000):
    
    if len(bubbles) == 0: return
    insert_aggregate_nodes(bubbles, "Bubble", batch_size)
    insert_aggregate_nodes(chains, "Chain", batch_size)
    insert_aggregate_links(bubbles, chains, batch_size)
    
    modify.adjust_compacted_nodes()

    max_depth = max([x["depth"] for x in chains + bubbles])

    print("      Calculating aggregate properties...")

    add_child_information(max_depth)
    add_position_information(max_depth)
    add_haplotype_information(max_depth)
