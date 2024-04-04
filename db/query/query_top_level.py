from db.neo4j_db import get_session
import db.utils.create_record as record
import db.utils.integrity_check as integrity


def get_top_level_aggregates(db, session, genome, chrom, start, end):
    nodes,links = [],[]

    query = """
            MATCH (n:Chain|Bubble)
            WHERE n.db = $db AND n.genome = $genome AND n.chrom = $chrom 
                AND n.start <= $end AND n.end >= $start AND NOT EXISTS {
                    MATCH (n)-[:INSIDE|PARENT]->(m)
                    WHERE m.chrom = $chrom AND m.start <= $end AND m.end >= $start
            }
            OPTIONAL MATCH (n)-[r:END]-(e:Segment)
            RETURN n, labels(n) AS type, collect(DISTINCT r) AS links
            """
    parameters = {"start": start, "end": end, "db": db, "genome": genome, "chrom": chrom}
    results = session.run(query, parameters)

    for result in results:
        nodes.append( record.node_record(result["n"], result["type"][0]) )
        links.extend( [record.link_record_simple(r) for r in result["links"]] )

    return nodes, links

def get_top_level_segments(db, session, genome, chrom, start, end):
    nodes,links = [],[]

    query = """
            MATCH (n:Segment)
            WHERE n.db = $db AND n.genome = $genome AND n.chrom = $chrom 
                AND n.start <= $end AND n.end >= $start AND NOT EXISTS {
                    MATCH (n)-[:INSIDE|PARENT]->(m)
                    WHERE m.chrom = $chrom AND m.start <= $end AND m.end >= $start
            }
            OPTIONAL MATCH (n)-[r:LINKS_TO]-(s:Segment)
            RETURN n, s, collect(DISTINCT r) AS links
            """

    parameters = {"start": start, "end": end, "db": db, "genome": genome, "chrom": chrom}
    results = session.run(query, parameters)

    collected_nodes = set()
    for result in results:
        node = record.segment_record(result["n"])
        if node["nodeid"] not in collected_nodes:
            nodes.append(node)
            collected_nodes.add(node["nodeid"])

        links.extend( [record.link_record_simple(r) for r in result["links"]] )

    return nodes, links


def get_top_level(genome, chrom, start, end):

    with get_session() as (db, session):
        aggregates,aggregateLinks = get_top_level_aggregates(db, session, genome, chrom, start, end)
        print(len(aggregates))

        segments,segmentLinks = get_top_level_segments(db, session, genome, chrom, start, end)

    nodes = aggregates + segments
    links = aggregateLinks + segmentLinks

    nodes = integrity.deduplicate_nodes(nodes)
    links = integrity.deduplicate_links(links)
    links = integrity.remove_invalid_links(nodes, links)

    print(f"TOP LEVEL QUERY: {chrom}:{start}-{end}")
    print(f"   Nodes: C+B={len(aggregateLinks)}, S={len(segments)}")
    print(f"   Links: C+B={len(aggregateLinks)}, S={len(segmentLinks)}")
    
    graph = {"nodes": nodes, "links": links}

    return graph