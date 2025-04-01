import numpy as np
from db.neo4j_db import get_session

def get_chromosome_spans(db, session):
    result = session.run("""
        MATCH (s:Segment {db: $db})
        RETURN s.genome AS genome, s.chrom AS chrom, min(s.start) AS min_start, max(s.end) AS max_end
    """, {"db": db})
    return result.data()


def create_clusters_for_level(session, db, window_bp, level, source_label, start_prop, end_prop):
    
    chrom_info = get_chromosome_spans(db, session)

    for row in chrom_info:
        genome = row["genome"]
        chrom = row["chrom"]
        start = row["min_start"]
        end = row["max_end"]

        if start is None or end is None:
            continue

        for bin_start in range(start, end, window_bp):
            bin_end = bin_start + window_bp
            bin_id = bin_start // window_bp
            
            #print(f"📦 Level {level}: {genome} {chrom} ({bin_start}-{bin_end})")

            # Query nodes for this bin
            result = session.run(f"""
                MATCH (n:{source_label} {{
                    db: $db,
                    genome: $genome,
                    chrom: $chrom
                }})
                WHERE n.{start_prop} < $bin_end AND n.{end_prop} >= $bin_start
                RETURN n.x1 AS x1, n.x2 AS x2, n.y1 AS y1, n.y2 AS y2
            """, {
                "db": db,
                "genome": genome,
                "chrom": chrom,
                "bin_start": bin_start,
                "bin_end": bin_end
            })

            rows = result.data()
            if not rows:
                continue

            x1s = np.array([r["x1"] for r in rows])
            x2s = np.array([r["x2"] for r in rows])
            y1s = np.array([r["y1"] for r in rows])
            y2s = np.array([r["y2"] for r in rows])

            cluster_id = f"{db}:{genome}:{chrom}:{bin_id}:{window_bp}"
            cluster_props = {
                "db": db,
                "genome": genome,
                "chrom": chrom,
                "bin": bin_id,
                "window": window_bp,
                "level": level,
                "start": bin_start,
                "end": bin_end,
                "id": cluster_id,
                "x1": float(np.mean(x1s) - np.std(x1s)),
                "x2": float(np.mean(x2s) + np.std(x2s)),
                "y1": float(np.mean(y1s) - np.std(y1s)),
                "y2": float(np.mean(y2s) + np.std(y2s)),
            }

            session.run("""
                MERGE (c:Cluster {
                    db: $db, genome: $genome, chrom: $chrom, bin: $bin, window: $window
                })
                ON CREATE SET c.start = $start, c.end = $end,
                              c.x1 = $x1, c.x2 = $x2,
                              c.y1 = $y1, c.y2 = $y2,
                              c.level = $level,
                              c.id = $id
            """, cluster_props)


def generate_clusters(window_bp=10_000, large_window_bp=1_000_000):
    with get_session() as (db, session):

        #print("🧹 Removing existing Cluster nodes and relationships...")
        #session.run("MATCH (c:Cluster {db: $db}) DETACH DELETE c", {"db": db})

        # Level 1: from Segments
        #create_clusters_for_level(
        #    session=session,
        #    db=db,
        #    window_bp=window_bp,
        #    level=1,
        #    source_label="Segment",
        #    start_prop="start",
        #    end_prop="end"
        #)

        chrom_info = get_chromosome_spans(db, session)

        session.run("""
            MATCH (c:Cluster {db: $db})
            WHERE c.level = 2
            DETACH DELETE c
        """, {"db": db})


        # Level 2: from level 1 Clusters
        create_clusters_for_level(
            session=session,
            db=db,
            window_bp=large_window_bp,
            level=2,
            source_label="Cluster",
            start_prop="start",
            end_prop="end"
        )