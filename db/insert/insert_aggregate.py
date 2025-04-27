from db.neo4j_db import get_session
from collections import defaultdict
import sys

import db.modify.preprocess_modifications as modify

def insert_aggregate_nodes(aggregates, type, batch_size):
    total = len(aggregates)
    
    with get_session(collection=True) as (db, collection, session):

        prefix = "b" if type.lower() == "bubble" else "c"    

        for i in range(0, total, batch_size):
            batch = aggregates[i:i + batch_size]

            sys.stdout.write(f"\r      Inserting {type}s: {min(i + batch_size, total)}/{total}.")

            query = f"""
                UNWIND $aggregates AS agg
                CREATE (:{type} {{
                    uuid: $db + ':' + $col + ':' + '{prefix}' + toString(agg.id),
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

        print(f"\r      Inserting Bubble & Chain links...")

        def insert_link(links, label_a, label_b, rel):
            query = f"""
                UNWIND $links AS link
                MATCH (a:{label_a} {{uuid: link.uuid_a}}),
                      (b:{label_b} {{uuid: link.uuid_b}})
                CREATE (a)-[:{rel}]->(b)
            """
            session.run(query, {"links": links})

        for bubble in bubbles:
            bubble_uuid = f"{db}:{collection}:b{bubble['id']}"
            start_uuid = f"{db}:{collection}:{bubble['ends'][0]}"
            end_uuid = f"{db}:{collection}:{bubble['ends'][1]}"

            linkmap["Segment.END.Bubble"].append({"uuid_a": start_uuid, "uuid_b": bubble_uuid})
            linkmap["Bubble.END.Segment"].append({"uuid_a": bubble_uuid, "uuid_b": end_uuid})

            if bubble["sb"]:
                sb_uuid = f"{db}:{collection}:b{bubble['sb']}"
                linkmap["Bubble.INSIDE.Bubble"].append({"uuid_a": bubble_uuid, "uuid_b": sb_uuid})

            for sid in bubble["inside"]:
                inside_uuid = f"{db}:{collection}:{sid}"
                linkmap["Segment.INSIDE.Bubble"].append({"uuid_a": inside_uuid, "uuid_b": bubble_uuid})

        for chain in chains:
            chain_uuid = f"{db}:{collection}:c{chain['id']}"
            start_uuid = f"{db}:{collection}:{chain['ends'][0]}"
            end_uuid = f"{db}:{collection}:{chain['ends'][1]}"

            linkmap["Segment.CHAIN_END.Chain"].append({"uuid_a": start_uuid, "uuid_b": chain_uuid})
            linkmap["Chain.CHAIN_END.Segment"].append({"uuid_a": chain_uuid, "uuid_b": end_uuid})

            if chain["sb"]:
                sb_uuid = f"{db}:{collection}:b{chain['sb']}"
                linkmap["Chain.PARENT_SB.Bubble"].append({"uuid_a": chain_uuid, "uuid_b": sb_uuid})

            for bid_inside in chain["inside"]:
                inside_uuid = f"{db}:{collection}:b{bid_inside}"
                linkmap["Bubble.CHAINED.Chain"].append({"uuid_a": inside_uuid, "uuid_b": chain_uuid})

        for key, batch in linkmap.items():
            if not batch:
                continue
            label_a, rel, label_b = key.split('.')
            for i in range(0, len(batch), batch_size):
                insert_link(batch[i:i + batch_size], label_a, label_b, rel)

def get_ids_at_depth(atype, session, params):
    id_query = """
        MATCH (a:"""+atype+""")
        WHERE a.db = $db AND a.collection = $col AND a.depth = $depth
        RETURN a.uuid AS uuid
    """
    return [r["uuid"] for r in session.run(id_query, params)]

def add_child_information(max_depth, batch_size=50000):
    with get_session(collection=True) as (db, collection, session):
        
        queries = [
            "WITH a, MIN(n.start) AS start SET a.start = start",
            "WITH a, MAX(n.end) AS end SET a.end = end",
            "WITH a, SUM(n.length) AS length SET a.length = length",
            "WITH a, MAX(n.length) AS largest SET a.largest_child = largest",
            "WITH a, COUNT(*) AS children SET a.children = children",
            "WITH a, head(collect(n.genome)) AS genome SET a.genome = genome",
            "WITH a, head(collect(n.chrom)) AS chrom SET a.chrom = chrom",
            "WITH a, SUM(CASE WHEN n.is_ref THEN 1 ELSE 0 END) > 0 AS has_ref SET a.is_ref = has_ref",
            "WITH a, SUM(n.gc_count) AS count SET a.gc_count = count",
        ]

        match_bubble = f"UNWIND $batch AS uuid MATCH (n)-[:INSIDE]->(a:Bubble) WHERE a.uuid = uuid"
        match_chain = f"UNWIND $batch AS uuid MATCH (n)-[:CHAINED]->(a:Chain) WHERE a.uuid = uuid"

        print("   👶 Adding child information to aggregate nodes...")

        for d in range(max_depth + 1):
            params = {"db": db, "col": collection, "depth": d}
            bubble_ids = get_ids_at_depth("Bubble", session, params)
            for i in range(0, len(bubble_ids), batch_size):
                params["batch"] = bubble_ids[i:i + batch_size]
                for query in queries:
                    session.run(f"{match_bubble} {query}", params)

            chain_ids = get_ids_at_depth("Chain", session, params)
            for i in range(0, len(chain_ids), batch_size):
                params["batch"] = chain_ids[i:i + batch_size]
                for query in queries:
                    session.run(f"{match_chain} {query}", params)


def add_position_information(max_depth, batch_size=50000):
    with get_session(collection=True) as (db, collection, session):

        match_bubble = "UNWIND $batch AS uuid MATCH (n)-[:INSIDE]->(a:Bubble) WHERE a.uuid = uuid"
        match_chain = "UNWIND $batch AS uuid MATCH (n)-[:CHAINED]->(a:Chain) WHERE a.uuid = uuid"

        query = """
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
        
        print("   📍Adding position information to aggregate nodes...")

        for d in range(max_depth + 1):
            params = {"db": db, "col": collection, "depth": d}

            bubble_ids = get_ids_at_depth("Bubble", session, params)
            for i in range(0, len(bubble_ids), batch_size):
                params["batch"] = bubble_ids[i:i + batch_size]
                session.run(f"{match_bubble} {query}", params)

            chain_ids = get_ids_at_depth("Chain", session, params)
            for i in range(0, len(chain_ids), batch_size):
                params["batch"] = chain_ids[i:i + batch_size]
                session.run(f"{match_chain} {query}", params)

def add_haplotype_information(max_depth, batch_size=50000):
    with get_session(collection=True) as (db, collection, session):

        hap_query_bubble_links_to = """
            UNWIND $batch AS uuid
            MATCH (s:Segment)-[l:LINKS_TO]-(s2), 
                  (s)-[:INSIDE]->(a:Bubble)
            WHERE a.uuid = uuid
              AND l.haplotype IS NOT NULL
            RETURN a.uuid AS uuid, l.haplotype AS hap
        """

        hap_query_bubble_end = """
            UNWIND $batch AS uuid
            MATCH (n)-[e:END]-(b:Bubble)-[:INSIDE]->(a:Bubble)
            WHERE a.uuid = uuid
              AND e.haplotype IS NOT NULL
            RETURN a.uuid AS uuid, e.haplotype AS hap
        """

        hap_write_bubble = """
            UNWIND $batch AS item
            MATCH (a:Bubble)
            WHERE a.uuid = item.uuid
            MATCH (s:Segment)-[e:END]-(a)
            SET e.haplotype = item.hap
        """

        hap_query_chain = """
            UNWIND $batch AS uuid
            MATCH (n)-[e:END]-(b:Bubble)-[:CHAINED]->(a:Chain)
            WHERE a.uuid = uuid
              AND e.haplotype IS NOT NULL
            RETURN a.uuid AS uuid, e.haplotype AS hap
        """

        hap_write_chain = """
            UNWIND $batch AS item
            MATCH (a:Chain)
            WHERE a.uuid = item.uuid
            MATCH (s:Segment)-[e:CHAIN_END]-(a)
            SET e.haplotype = item.hap
        """

        def calculate_haplotypes(results):
            hap_map = defaultdict(int)
            for result in results:
                for record in result:
                    uuid = record["uuid"]
                    hap_hex = record["hap"]
                    hap_map[uuid] |= int(hap_hex, 16)

                haps = []
                for uuid in hap_map:
                    hmap = {"uuid": uuid, "hap": hex(hap_map[uuid])[2:]}
                    haps.append(hmap)
            return haps

        print("   🪢Adding haplotype information to aggregate nodes...")

        for d in range(max_depth + 1):
            params = {"db": db, "col": collection, "depth": d}

            bubble_ids = get_ids_at_depth("Bubble", session, params)
            for i in range(0, len(bubble_ids), batch_size):
                params["batch"] = bubble_ids[i:i + batch_size]

                result1 = session.run(hap_query_bubble_links_to, params)
                result2 = session.run(hap_query_bubble_end, params)
                params["batch"] = calculate_haplotypes([result1, result2])
                session.run(hap_write_bubble, params)

            chain_ids = get_ids_at_depth("Chain", session, params)
            for i in range(0, len(chain_ids), batch_size):
                params["batch"] = chain_ids[i:i + batch_size]
                result1 = session.run(hap_query_chain, params)
                params["batch"] = calculate_haplotypes([result1])
                session.run(hap_write_chain, params)

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
