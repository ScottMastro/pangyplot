from db.neo4j_db import get_session
import db.utils.create_record as record
from db.utils.integrity_check import deduplicate_links

def get_subgraph_nodes(nodeid, genome, chrom, start, end):
    nodes,links = [],[]
    with get_session() as (db, session):

        # todo: strict fails to get nodes w/o start and end positions (add genome)
        strict = "WHERE n.chrom = $chrom AND n.start <= $end AND n.end >= $start AND ID(t) = $i AND NOT EXISTS {"
        lax = "WHERE n.db = $db AND ID(t) = $i AND NOT EXISTS {"
        query = """
                MATCH (n)-[:PARENT|INSIDE]->(t)
                """+strict+"""
                    MATCH (n)-[:PARENT|INSIDE]->(m)
                    WHERE ID(m) <> ID(t) AND (m)-[:PARENT|INSIDE*]->(t)
                }
                OPTIONAL MATCH (n)-[r1:END]-(s1:Segment)
                OPTIONAL MATCH (n)-[r2:LINKS_TO]-(s2:Segment)
                RETURN n, labels(n) AS type, collect(DISTINCT r1) AS ends, collect(DISTINCT r2) AS links
                """

        parameters = {"db": db, "i": nodeid, "start": start, "end": end, "genome": genome, "chrom": chrom}
        results = session.run(query, parameters)

        for result in results:
            nodes.append( record.node_record(result["n"], result["type"][0]) )
            lastType = result["type"][0]
            links.extend( [record.link_record_simple(r) for r in result["ends"]] )
            links.extend( [record.link_record_simple(r) for r in result["links"]] )

    # trivial case where bubble chain has only one bubble
    # pop the bubble immediately
    if len(nodes) == 1 and lastType == "Bubble":
        print("trivial case")
        return get_subgraph_nodes(nodes[0]["nodeid"], genome, chrom, start, end)

    return nodes, deduplicate_links(links)

def get_subgraph_simple(nodeid):
    nodes,links = [],[]
    with get_session() as (db, session):

        query = """
                MATCH (t)<-[:PARENT|INSIDE*]-(n)
                WHERE n.db = $db AND ID(t) = $i AND n.subtype <> "super" AND NOT EXISTS {
                    MATCH (n)-[:PARENT|INSIDE]->(m)
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



'''
from db.neo4j_db import get_session
import db.utils.create_record as record
from db.utils.integrity_check import deduplicate_links

def get_subgraph_nodes(session, type, nodeid, chrom, start, end):
    nodes,links = [],[]

    query = """
            MATCH (n:"""+type+""")-[:PARENT|INSIDE]->(t)
            WHERE n.chrom = $chrom AND n.start <= $end AND n.end >= $start AND ID(t) = $i AND  NOT EXISTS {
                MATCH (n)-[:PARENT|INSIDE]->(m)
                WHERE ID(m) <> ID(t) AND (m)-[:PARENT|INSIDE*]->(t)                
            }
            OPTIONAL MATCH (n)-[r1:END]-(s1:Segment)
            OPTIONAL MATCH (n)-[r2:LINKS_TO]-(s2:Segment)
            RETURN n, labels(n) AS type, collect(DISTINCT r1) AS ends, collect(DISTINCT r2) AS links
            """

    parameters = {"i": nodeid, "start": start, "end": end, "chrom": chrom}
    results = session.run(query, parameters)

    for result in results:
        nodes.append( record.node_record(result["n"], result["type"][0]) )
        links.extend( [record.link_record_simple(r) for r in result["ends"]] )
        links.extend( [record.link_record_simple(r) for r in result["links"]] )

    # trivial case where bubble chain has only one bubble
    if len(nodes) == 1 and type == "Bubble":
        print("trivial case")
        return get_subgraph_nodes(session, type, nodes[0]["nodeid"], chrom, start, end)

    return nodes, deduplicate_links(links)

def get_subgraph_simple(nodeid, type):
    nodes,links = [],[]
    with get_session() as session:

        query = """
                MATCH (t)<-[:PARENT|INSIDE*]-(n:"""+type+""")
                WHERE ID(t) = $i AND n.subtype <> "super" AND NOT EXISTS {
                    MATCH (n)-[:PARENT|INSIDE]->(m)
                    WHERE m.subtype <> "super"
                }
                OPTIONAL MATCH (n)-[r:END]-(s:Segment)
                RETURN n, s, labels(n) AS type, collect(DISTINCT r) AS ends
                """
        results = session.run(query, {"i": nodeid})

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
   
def get_subgraph_chains(session, nodeid, chrom, start, end):
    return get_subgraph_nodes(session, "Chain", nodeid, chrom, start, end)
def get_subgraph_bubbles(session, nodeid, chrom, start,  end):
    return get_subgraph_nodes(session, "Bubble", nodeid, chrom, start, end)
def get_subgraph_segments(session, nodeid, chrom, start,  end):
    return get_subgraph_nodes(session, "Segment", nodeid, chrom, start, end)

def get_subgraph(nodeid, chrom, start, end):

    with get_session() as session:
        chains,chainLinks = get_subgraph_chains(session, nodeid, chrom, start,  end)
        bubbles,bubbleLinks = get_subgraph_bubbles(session, nodeid, chrom, start,  end)
        segments,segmentLinks = get_subgraph_segments(session, nodeid, chrom, start,  end)

    print(f"SUBGRAPH QUERY {nodeid}: {chrom}:{start}-{end}")
    print(f"   Nodes: C={len(chains)}, B={len(bubbles)}, S={len(segments)}")
    print(f"   Links: C={len(chainLinks)}, B={len(bubbleLinks)}, S={len(segmentLinks)}")

    subgraph = {"nodes": chains + bubbles + segments, 
            "links": chainLinks + bubbleLinks + segmentLinks}

    return subgraph

'''