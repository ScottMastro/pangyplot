from db.neo4j_db import get_session
import db.utils.create_record as record
from db.utils.integrity_check import deduplicate_links, remove_invalid_links


def get_top_level_aggregates(session, type, chrom, start, end):
    nodes,links = [],[]

    query = """
            MATCH (n:"""+type+""")
            WHERE n.start <= $end AND n.end >= $start AND n.chrom = $chrom AND NOT EXISTS {
                MATCH (n)-[:INSIDE|PARENT]->(m)
                WHERE m.start <= $end AND m.end >= $start AND m.chrom = $chrom
            }
            OPTIONAL MATCH (n)-[r1:END]-(s1:Segment)
            OPTIONAL MATCH (n)-[r2:LINKS_TO]-(s2:Segment)
            RETURN n, labels(n) AS type, collect(DISTINCT r1) AS ends, collect(DISTINCT r2) AS links
            """

    parameters = {"start": start, "end": end, "chrom": chrom}
    results = session.run(query, parameters)

    for result in results:
        nodes.append( record.node_record(result["n"], result["type"][0]) )
        links.extend( [record.link_record_simple(r) for r in result["ends"]] )
        links.extend( [record.link_record_simple(r) for r in result["links"]] )

    links = remove_invalid_links(nodes, links)
    links = deduplicate_links(links)

    return nodes, links

def get_top_level_chains(session, chrom, start, end):
    return get_top_level_aggregates(session, "Chain", chrom, start, end)
def get_top_level_bubbles(session, chrom, start, end):
    return get_top_level_aggregates(session, "Bubble", chrom, start, end)
def get_top_level_segments(session, chrom, start, end):
    return get_top_level_aggregates(session, "Segment", chrom, start, end)

#todo: delete?
def get_top_level_segments2(session, chrom, start, end):
    segments,links = [],[]

    # NOTE: we find all segments that overlap the range, but only look for bubbles fully contained
    query = """
            MATCH (s:Segment)
            WHERE s.start <= $end AND s.end >= $start AND s.chrom = $chrom AND NOT EXISTS {
                MATCH (s)-[:INSIDE]->(n)
                WHERE n.start >= $start AND n.end <= $end AND n.chrom = $chrom
            }
            MATCH (s)-[r:LINKS_TO]->(m:Segment) 
            RETURN s, collect(r) AS links
            """
    parameters = {"start": start, "end": end, "chrom": chrom}
    results = session.run(query, parameters)


    for result in results:
        segments.append( record.segment_record(result["s"]) )
        links.extend( [record.link_record_simple(r) for r in result["links"]] )

    segIds={s["nodeid"] for s in segments}
    keepLinks = []
    for link in links:
        if link["target"] not in segIds or link["source"] not in segIds:
            continue
        keepLinks.append(link)

    return segments, keepLinks

def get_top_level(chrom, start, end):

    with get_session() as session:

        chains,chainLinks = get_top_level_chains(session, chrom, start, end)
        bubbles,bubbleLinks = get_top_level_bubbles(session, chrom, start, end)
        segments,segmentLinks = get_top_level_segments(session, chrom, start, end)

    print(f"TOP LEVEL QUERY: {chrom}:{start}-{end}")
    print(f"   Nodes: C={len(chains)}, B={len(bubbles)}, S={len(segments)}")
    print(f"   Links: C={len(chainLinks)}, B={len(bubbleLinks)}, S={len(segmentLinks)}")
    
    graph = {"nodes": chains + bubbles + segments, 
            "links": chainLinks + bubbleLinks + segmentLinks}

    return graph