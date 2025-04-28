from db.neo4j_db import get_session
import db.utils.create_record as record
import db.utils.integrity_check as integrity

def get_node_type(nodeid):
    with get_session() as (db, session):

        node_type_query = """
        MATCH (n) WHERE n.db = $db AND ID(n) = $i
        RETURN labels(n) AS labels
        """
        result = session.run(node_type_query, {"db": db, "i": nodeid,})
        labels = result.single()["labels"]
        if not labels:
            return None

        return labels[0]

def get_subgraph_nodes(nodeid, genome, chrom, start, end):
    nodes, links = [], []

    with get_session() as (db, session):

        node_type = get_node_type(nodeid)
        if node_type is None:
            return nodes, links
        
        parameters = {"db": db, "i": nodeid, "start": start, "end": end, "genome": genome, "chrom": chrom}

        if node_type == "Bubble":
            query = """
                    MATCH (n)-[i:INSIDE]->(t:Bubble)
                    WHERE t.db = $db AND ID(t) = $i

                    OPTIONAL MATCH (n)-[l1:LINKS_TO]-(:Segment)
                    OPTIONAL MATCH (n)-[r:END]-(e:Segment)
                    OPTIONAL MATCH (e)-[l2:LINKS_TO]-(:Segment)
                    OPTIONAL MATCH (e)-[:COMPACT]-(c:Segment)
                    OPTIONAL MATCH (c)-[l3:LINKS_TO]->(:Segment)

                    RETURN n, i, 
                        labels(n) AS type,
                        collect(DISTINCT l1) + collect(DISTINCT l2) + collect(DISTINCT l3) AS links,
                        collect(DISTINCT r) AS endlinks
                    """
            results = session.run(query, parameters)
            for result in results:
                node = record.node_record(result["n"], result["type"][0])

                node["bubble"] = nodeid
                nodes.append(node)

                for r in result["endlinks"] + result["links"]:
                    link = record.link_record(r)
                    if link:
                        links.append(link)

        elif node_type == "Chain":
            query = """
                    MATCH (b:Bubble)-[:CHAINED]->(t:Chain)
                    WHERE t.db = $db AND ID(t) = $i
                    WITH b, t
                    OPTIONAL MATCH (b)-[r1:END]-(e:Segment)
                    OPTIONAL MATCH (t)-[r2:CHAIN_END]-(s1:Segment)
                    OPTIONAL MATCH (e)-[:COMPACT]-(c:Segment)
                    OPTIONAL MATCH (e)-[l1:LINKS_TO]->(target1:Segment)
                    OPTIONAL MATCH (c)-[l2:LINKS_TO]->(target2:Segment)

                    RETURN b, e, collect(DISTINCT c) AS compacted_segments,
                        collect(DISTINCT r1) AS endlinks, collect(DISTINCT r2) AS chainlinks,
                        collect(DISTINCT l1) + collect(DISTINCT l2) AS compactlinks
                    """

            results = session.run(query, parameters)

            for result in results:
                bubble = record.bubble_record(result["b"])
                bubble["chain"] = nodeid
                nodes.append(bubble)

                node = record.segment_record(result["e"])
                node["chain"] = nodeid
                nodes.append(node)

                compacted_segments = result["compacted_segments"] or []
                for seg in compacted_segments:
                    cnode = record.segment_record(seg)
                    cnode["chain"] = nodeid
                    nodes.append(cnode)

                for r in result["endlinks"]:
                    link = record.link_record(r)
                    if link:
                        links.append(link)

                for r in result["chainlinks"]:
                    link = record.link_record(r)
                    if link:
                        links.append(link)

                compact_links = result["compactlinks"] or []
                links.extend([record.link_record(link) for link in compact_links])

    nodes = integrity.deduplicate_nodes(nodes)
    links = integrity.deduplicate_links(links)
    #links = integrity.remove_invalid_links(nodes, links)

    return nodes, links


def get_subgraph_simple(nodeid):
    nodes,links = [],[]
    with get_session() as (db, session):

        query = """
                MATCH (t)<-[:INSIDE*]-(n)
                WHERE n.db = $db AND ID(t) = $i AND n.subtype <> "super" AND NOT EXISTS {
                    MATCH (n)-[:INSIDE]->(m)
                    WHERE m.subtype <> "super"
                }
                OPTIONAL MATCH (n)-[r:END]-(s:Segment)
                RETURN n, s, labels(n) AS type, collect(DISTINCT r) AS ends
                """
        results = session.run(query, {"db": db, "i": nodeid})

        for result in results:
            node = record.node_record(result["n"], result["type"][0])
            if node is not None:
                nodes.append(node)
            node = record.segment_record(result["s"])
            if node is not None:
                nodes.append(node)


            for result in results["ends"]:
                link = record.link_record_simple(result)
                links.append(link)

    print("nnodes", len(nodes))
    return nodes, links
   

def get_subgraph(nodeid, genome, chrom, start, end):
    nodes,links = get_subgraph_nodes(nodeid, genome, chrom, start, end)

    print(f"SUBGRAPH QUERY: ")#{chrom}:{start}-{end}")
    print(f"   Nodes: {len(nodes)}")
    print(f"   Links: {len(links)}")

    return {"nodes": nodes, "links": links}

