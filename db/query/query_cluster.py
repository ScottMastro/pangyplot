from db.neo4j_db import get_session
import db.utils.create_record as record

def get_clusters(genome, chrom, start, end, level=None, window=None):
    
    if level is None:
        level=1
        if abs(end-start) > 100_000:
            level=2

    with get_session() as (db, session):
        filters = ["c.db = $db", "c.genome = $genome", "c.chrom = $chrom", "c.end > $start", "c.start < $end"]
        params = {
            "db": db,
            "genome": genome,
            "chrom": chrom,
            "start": start,
            "end": end
        }

        if level is not None:
            filters.append("c.level = $level")
            params["level"] = level
        if window is not None:
            filters.append("c.window = $window")
            params["window"] = window

        where_clause = " AND ".join(filters)
        query = f"""
            MATCH (c:Cluster)
            WHERE {where_clause}
            RETURN c
        """

        result = session.run(query, params)        
        return { "clusters": [record.cluster_record(result["c"]) for record in result] }
