from db.db import get_session

def insert_segments(segments, batch_size=10000):
    if len(segments) == 0: return
    with get_session() as session:

        for i in range(0, len(segments), batch_size):
            batch = segments[i:i + batch_size]
            query = """
                UNWIND $batch AS segment
                CREATE (:Segment {
                    id: segment.id,
                    sequence: segment.seq,
                    chrom: segment.chrom,
                    start: segment.start,
                    end: segment.end,
                    x1: segment.x1,
                    y1: segment.y1,
                    y2: segment.y2,
                    x2: segment.x2,
                    length: segment.length
                })
            """
            session.run(query, {"batch": batch})

def insert_segment_links(links, batch_size=10000):
    if len(links) == 0: return
    with get_session() as session:

        for i in range(0, len(links), batch_size):
            batch = links[i:i + batch_size]
            query = """
            UNWIND $batch AS link
            MATCH (a:Segment {id: link.from_id}), (b:Segment {id: link.to_id})
            CREATE (a)-[:LINKS_TO {
                from_strand: link.from_strand,
                to_strand: link.to_strand,
                haplotype: link.haplotype,
                frequency: link.frequency}]->(b)
            """
            session.run(query, {"batch": batch})




