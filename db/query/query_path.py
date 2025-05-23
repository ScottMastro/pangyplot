from db.neo4j_db import get_session
import re

def reconstruct_path(records):

    def decompress_chunk(chunk_str, base_offset):
        pattern = r'[><][0-9]+'
        tokens = re.findall(pattern, chunk_str)
        
        segments = []
        for token in tokens:
            strand = '+' if token[0] == '>' else '-'
            offset = int(token[1:])
            seg_id = base_offset + offset
            segments.append(f"{seg_id}{strand}")
        return segments

    path = []
    for record in sorted(records, key=lambda x: x["offset"]):
        path.extend(decompress_chunk(record["chunk"], base_offset=record["offset"]))

    return {
        "sample": records[0]["sample"],
        "contig": records[0]["contig"],
        "hap": records[0].get("haplotype"),
        "start": records[0]["start"],
        "path": path
    }

def query_path_chunks(session, db, sample, contig, node_ids, buffer_chunks=1, chunk_size=50):
    """
    Given a list of node IDs, find the relevant PathChunks in Neo4j.
    Groups node_ids into offset ranges and fetches surrounding chunks.
    """
    node_offsets = [nid // chunk_size for nid in node_ids]
    unique_offsets = sorted(set(node_offsets))

    ranges = []
    for offset in unique_offsets:
        for buf in range(-buffer_chunks, buffer_chunks + 1):
            ranges.append(offset + buf)

    query = """
        MATCH (p:PathChunk)
        WHERE p.db = $db AND p.sample = $sample AND p.contig = $contig AND p.offset IN $offsets
        RETURN p ORDER BY p.offset
    """
    result = session.run(query, parameters={
        "db": db,
        "sample": sample,
        "contig": contig,
        "offsets": list(set(ranges))
    })
    return [record["p"] for record in result]

