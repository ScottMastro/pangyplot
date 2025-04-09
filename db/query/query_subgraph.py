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
                MATCH (n)-[:INSIDE]->(t)
                """+lax+"""
                    MATCH (n)-[:INSIDE]->(m)
                    WHERE ID(m) <> ID(t) AND (m)-[:INSIDE*]->(t)
                }
                OPTIONAL MATCH (n)-[r1:END]-(s1:Segment)
                OPTIONAL MATCH (n)-[r2:LINKS_TO]-(s2:Segment)
                RETURN n, labels(n) AS type, collect(DISTINCT r1) AS endlinks, collect(DISTINCT r2) AS links
                """

        parameters = {"db": db, "i": nodeid, "start": start, "end": end, "genome": genome, "chrom": chrom}
        results = session.run(query, parameters)

        for result in results:
            nodes.append( record.node_record(result["n"], result["type"][0]) )
            
            for link in result["endlinks"]:
                if str(link.start_node.id) =="1907672" or str(link.end_node.id) == "1907672":
                    print(link)    
                links.extend([record.link_record(link)])

            #links.extend( [record.link_record(r) for r in result["endlinks"]] )
            links.extend( [record.link_record(r) for r in result["links"]] )

    return nodes, deduplicate_links(links)

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

