from db.neo4j_db import get_session
import db.record as record

def get_top_level(chrom, start, end):
    with get_session() as session:

        query = """
                MATCH (n)
                WHERE n.start >= $start AND n.end <= $end AND n.chrom = $chrom AND NOT EXISTS {
                    MATCH (n)-[:INSIDE|PARENT]->(m)
                    WHERE m.start >= $start AND m.end <= $end AND m.chrom = $chrom
                }
                MATCH (n)-[r:END]-(s:Segment)
                RETURN n, labels(n) AS type, collect(r) AS ends
                """

        parameters = {"start": start, "end": end, "chrom": chrom}
        result = session.run(query, parameters)

        nodes = record.node_records(result, "n", "type")
        links = record.link_records_simple(result, "ends")

    print("nnodes", len(nodes))
    return nodes, links


def get_top_level_segments(chrom, start, end):
    with get_session() as session:

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
        result = session.run(query, parameters)

        segments,links = [],[]

        segments = record.segment_records(result, "s", "type")
        links = record.link_records_simple(result, "links")

    segIds={s["nodeid"] for s in segments}
    keepLinks = []
    for link in links:
        if link["target"] not in segIds or link["source"] not in segIds:
            continue
        keepLinks.append(link)

    print("nsegs", len(segments))   
    return segments, keepLinks

