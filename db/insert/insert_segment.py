from db.neo4j_db import get_session

#todo: handle situation where different chromosomes have the same segment ids

def insert_segments(segments, batch_size=10000):
    if len(segments) == 0: 
        return
    
    with get_session() as (db, session):

        for i in range(0, len(segments), batch_size):
            batch = segments[i:i + batch_size]
            query = """
                UNWIND $batch AS segment
                CREATE (:Segment {
                    id: segment.id,
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
            session.run(query, parameters={"batch": batch, "db": db})

def insert_segment_links(links, batch_size=10000):
    if len(links) == 0: return
    with get_session() as (db,session):

        for i in range(0, len(links), batch_size):
            batch = links[i:i + batch_size]
            query = """
            UNWIND $batch AS link
            MATCH (a:Segment {id: link.from_id, db: $db}), (b:Segment {id: link.to_id, db: $db})            
            CREATE (a)-[:LINKS_TO {
                from_strand: link.from_strand,
                to_strand: link.to_strand,
                haplotype: link.haplotype,
                reverse: link.reverse,
                frequency: link.frequency,
                is_ref: link.is_ref
            }]->(b)
                
            """
            session.run(query, {"batch": batch, "db": db})


