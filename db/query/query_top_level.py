from db.neo4j_db import get_session
import db.utils.create_record as record
from db.utils.integrity_check import deduplicate_links, remove_invalid_links


def get_top_level_aggregates(db, session, type, genome, chrom, start, end):
    nodes,links = [],[]

    query = """
            MATCH (n:"""+type+""")
            WHERE n.db = $db AND n.start <= $end AND n.end >= $start AND n.chrom = $chrom AND NOT EXISTS {
                MATCH (n)-[:INSIDE|PARENT]->(m)
                WHERE m.start >= $start AND m.end <= $end AND m.chrom = $chrom
            }
            OPTIONAL MATCH (n)-[r1:END]-(s1:Segment)
            OPTIONAL MATCH (n)-[r2:LINKS_TO]-(s2:Segment)
            RETURN n, labels(n) AS type, collect(DISTINCT r1) AS ends, collect(DISTINCT r2) AS links
            """

    parameters = {"start": start, "end": end, "db": db, "genome": genome, "chrom": chrom}
    results = session.run(query, parameters)

    for result in results:
        nodes.append( record.node_record(result["n"], result["type"][0]) )
        links.extend( [record.link_record_simple(r) for r in result["ends"]] )
        links.extend( [record.link_record_simple(r) for r in result["links"]] )

    return nodes, links

def get_top_level_chains(db, session, genome, chrom, start, end):
    return get_top_level_aggregates(db, session, "Chain", genome, chrom, start, end)
def get_top_level_bubbles(db, session, genome, chrom, start, end):
    return get_top_level_aggregates(db, session, "Bubble", genome, chrom, start, end)
def get_top_level_segments(db, session, genome, chrom, start, end):
    return get_top_level_aggregates(db, session, "Segment", genome, chrom, start, end)


def get_top_level(genome, chrom, start, end):

    with get_session() as (db, session):
        print(db)
        chains,chainLinks = get_top_level_chains(db, session, genome, chrom, start, end)
        bubbles,bubbleLinks = get_top_level_bubbles(db, session, genome, chrom, start, end)
        segments,segmentLinks = get_top_level_segments(db, session, genome, chrom, start, end)

    nodes = chains + bubbles + segments
    links = chainLinks + bubbleLinks + segmentLinks

    links = remove_invalid_links(nodes, links)
    links = deduplicate_links(links)

    print(f"TOP LEVEL QUERY: {chrom}:{start}-{end}")
    print(f"   Nodes: C={len(chains)}, B={len(bubbles)}, S={len(segments)}")
    print(f"   Links: C={len(chainLinks)}, B={len(bubbleLinks)}, S={len(segmentLinks)}")
    
    graph = {"nodes": nodes, "links": links}

    return graph