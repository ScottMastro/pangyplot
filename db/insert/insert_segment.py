from db.neo4j_db import get_session

def insert_segments(segments, batch_size=10000):
    if len(segments) == 0: 
        return
    
    with get_session(collection=True) as (db, collection, session):

        for i in range(0, len(segments), batch_size):
            batch = segments[i:i + batch_size]
            query = """
                UNWIND $batch AS segment
                CREATE (:Segment {
                    uuid: $db + ':' + $col + ':' + segment.id,
                    id: segment.id,
                    collection: $col,
                    db: $db,
                    genome: segment.genome,
                    chrom: segment.chrom,
                    start: segment.start,
                    end: segment.end,
                    x1: segment.x1,
                    y1: segment.y1,
                    y2: segment.y2,
                    x2: segment.x2,
                    length: segment.length,
                    sequence: segment.seq,
                    gc_count: segment.gc_count,
                    is_ref: segment.is_ref

                })
            """
            session.run(query, parameters={"col": collection, "batch": batch, "db": db})

def insert_segment_links(links, batch_size=10000):
    if len(links) == 0:
        return

    with get_session(collection=True) as (db, collection, session):

        for i in range(0, len(links), batch_size):
            batch = links[i:i + batch_size]

            for link in batch:
                link["from_uuid"] = f"{db}:{collection}:{link['from_id']}"
                link["to_uuid"] = f"{db}:{collection}:{link['to_id']}"

            query = """
                UNWIND $batch AS link
                MATCH (a:Segment {uuid: link.from_uuid}),
                      (b:Segment {uuid: link.to_uuid})
                CREATE (a)-[:LINKS_TO {
                    from_strand: link.from_strand,
                    to_strand: link.to_strand,
                    haplotype: link.haplotype,
                    reverse: link.reverse,
                    frequency: link.frequency,
                    is_ref: link.is_ref
                }]->(b)
            """
            session.run(query, {"batch": batch})
