from db.neo4j_db import get_session
import db.utils.create_record as record
from db.utils.integrity_check import deduplicate_links, remove_invalid_links


def get_top_level_aggregates(db, session, genome, chrom, start, end):
    nodes,links = [],[]

    query = """
            MATCH (n:Chain|Bubble)
            WHERE n.db = $db AND n.genome = $genome AND n.chrom = $chrom 
                AND n.start <= $end AND n.end >= $start AND NOT EXISTS {
                    MATCH (n)-[:INSIDE|PARENT]->(m)
                    WHERE m.chrom = $chrom AND m.start >= $start AND m.end <= $end
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
                    WHERE m.chrom = $chrom AND m.start >= $start AND m.end <= $end
            }
            OPTIONAL MATCH (n)-[r:LINKS_TO]-(s:Segment)
            RETURN n,s, collect(DISTINCT r) AS links
            """

    parameters = {"start": start, "end": end, "db": db, "genome": genome, "chrom": chrom}
    results = session.run(query, parameters)

    for result in results:
        nodes.append( record.segment_record(result["n"]) )
        links.extend( [record.link_record_simple(r) for r in result["links"]] )

    return nodes, links


def get_top_level(genome, chrom, start, end):

    with get_session() as (db, session):
        print(db)
        aggregates,aggregateLinks = get_top_level_aggregates(db, session, genome, chrom, start, end)
        segments,segmentLinks = get_top_level_segments(db, session, genome, chrom, start, end)

    nodes = aggregates + segments
    links = aggregateLinks + segmentLinks

    links = remove_invalid_links(nodes, links)
    links = deduplicate_links(links)

    print(f"TOP LEVEL QUERY: {chrom}:{start}-{end}")
    print(f"   Nodes: C+B={len(aggregateLinks)}, S={len(segments)}")
    print(f"   Links: C+B={len(aggregateLinks)}, S={len(segmentLinks)}")
    
    graph = {"nodes": nodes, "links": links}

    return graph