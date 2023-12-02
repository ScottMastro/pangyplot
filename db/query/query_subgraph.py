from db.neo4j_db import get_session
import json
import db.utils.create_record as record

#singleton chain
"""
MATCH (b:Bubble)-[:INSIDE|PARENT]->(c:Chain)
WHERE NOT EXISTS {
    MATCH (b2:Bubble)-[:INSIDE|PARENT]->(c)
    WHERE ID(b2) <> ID(b)
}
RETURN b,c LIMIT 200
"""

def query_all_segments():
    batch_size=100000
    nodes = []

    with get_session() as session:
        skip = 0
        while True:
            query = """
                    MATCH (s:Segment)
                    RETURN s.id, s.length
                    SKIP $skip
                    LIMIT $limit
                    """
            results = session.run(query, skip=skip, limit=batch_size)
            batch = [(record['s.id'], record['s.length']) for record in results]

            if not batch:
                break
            nodes.extend(batch)
            skip += batch_size
    return nodes

def query_all_links():
    batch_size=100000
    links = []
    with get_session() as session:
        skip = 0
        while True:
            query = """
                    MATCH (s1:Segment)-[l:LINKS_TO]->(s2:Segment)
                    RETURN l.from_strand, l.to_strand, s1.id, s2.id
                    SKIP $skip
                    LIMIT $limit
                    """
            results = session.run(query, skip=skip, limit=batch_size)
            batch = [(result['l.from_strand'], result['s1.id'], result['l.to_strand'], result['s2.id']) for result in results]
    
            if not batch:
                break 
            
            links.extend(batch)
            skip += batch_size

    return links

def get_subgraph(nodeid):
    nodes,links = [],[]
    with get_session() as session:

        query = """
                MATCH (n)-[:PARENT|INSIDE]->(t)
                WHERE ID(t) = $i AND NOT EXISTS {
                    MATCH (n)-[:PARENT|INSIDE]->(m)
                    WHERE ID(m) <> ID(t) AND (m)-[:PARENT|INSIDE*]->(t)                
                }
                OPTIONAL MATCH (n)-[r1:END]-(s1:Segment)
                OPTIONAL MATCH (n)-[r2:LINKS_TO]-(s2:Segment)
                RETURN n, labels(n) AS type, collect(DISTINCT r1) AS ends, collect(DISTINCT r2) AS links
                """
        results = session.run(query, {"i": nodeid})

        ends = record.link_records_simple(results, "ends")
        links = record.link_records_simple(results, "links")

        for result in results:
            node = result.node_record(result["n"], result["type"][0])
            if node is not None:
                nodes.append(node)


    print("nnodes", len(nodes))
    return nodes, ends+links

def get_subgraph_simple(nodeid):
    nodes,links = [],[]
    with get_session() as session:

        query = """
                MATCH (t)<-[:PARENT|INSIDE*]-(n)
                WHERE ID(t) = $i AND n.subtype <> "super" AND NOT EXISTS {
                    MATCH (n)-[:PARENT|INSIDE]->(m)
                    WHERE m.subtype <> "super"
                }
                OPTIONAL MATCH (n)-[r:END]-(s:Segment)
                RETURN n, s, labels(n) AS type, collect(DISTINCT r) AS ends
                """
        results = session.run(query, {"i": nodeid})

        for result in results:
            node = record.node_record(result["n"], result["type"][0])
            if node is not None:
                nodes.append(node)
            node = record.segment_record(result["s"])
            if node is not None:
                nodes.append(node)


            for result in results["ends"]:
                link = record.link_record_simple(result)
                links.append(link)

    print("nnodes", len(nodes))
    return nodes, links

def get_bubble_subgraph(nodeid):
    with get_session() as session:

        query = """
            MATCH (s:Segment)-[r1:INSIDE]->(b:Bubble)
            WHERE ID(b) = $i
            MATCH (s)-[r:LINKS_TO]-(s2:Segment)
            RETURN s, b, collect(r) AS links
            """
        results = session.run(query, {"i": nodeid})

        segments,links = [],[]

        for result in results:
            for r in result["links"]:
                link = record.link_record_simple(r)
                links.append(link)

            segment = record.segment_record(result["s"]) 
            segments.append(segment)

    print("nsegs", len(segments))
    return segments, links
    

def get_top_level_chains(chrom, start, end):
    with get_session() as session:

        query = """
            MATCH (c:Chain)
            WHERE c.start >= $start AND c.end <= $end AND c.chrom = $chrom AND NOT EXISTS {
                    MATCH (c)-[:PARENT]->(n)
                    WHERE n.start >= $start AND n.end <= $end AND n.chrom = $chrom
                }
            MATCH (c)-[r:END]-(s:Segment)
            RETURN c, collect(r) AS ends
            """
        parameters = {"start": start, "end": end, "chrom": chrom}
        results = session.run(query, parameters)

        chains,links = [],[]

        for result in results:
            for r in result["ends"]:
                link = record.link_record_simple(r)
                links.append(link)

            chain = record.chain_record(result["c"]) 
            chains.append(chain)


    print("nchains", len(chains))
    return chains, links


def get_top_level_bubbles(chrom, start, end):
    with get_session() as session:

        query = """
                MATCH (b:Bubble)
                WHERE b.start >= $start AND b.end <= $end AND b.chrom = $chrom AND NOT EXISTS {
                    MATCH (b)-[:INSIDE]->(c:Chain)
                    WHERE c.start >= $start AND c.end <= $end AND c.chrom = $chrom
                }
                MATCH (b)-[r:END]-(s:Segment)
                RETURN b, collect(r) AS ends
                """
        parameters = {"start": start, "end": end, "chrom": chrom}
        results = session.run(query, parameters)

        bubbles,links = [],[]

        for result in results:
            for r in result["ends"]:
                link = record.link_record_simple(r)
                links.append(link)

            bubble = record.bubble_record(result["b"]) 
            bubbles.append(bubble)
    print("nbubs", len(bubbles))
    return bubbles,links


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
        results = session.run(query, parameters)

        segments,links = [],[]

        for result in results:
            for r in result["links"]:
                link = record.link_record_simple(r)
                links.append(link)

            segment = record.segment_record(result["s"]) 
            segments.append(segment)

    segIds={s["nodeid"] for s in segments}
    keepLinks = []
    for link in links:
        if link["target"] not in segIds or link["source"] not in segIds:
            continue
        keepLinks.append(link)

    print("nsegs", len(segments))   
    return segments, keepLinks


def get_segments(chrom, start, end):
    data = []

    with get_session() as session:

        query = f"""
        MATCH (n:Segment)
        WHERE n.pos >= {start} AND n.pos <= {end} AND n.chrom = "{chrom}"
        WITH collect(n) as baseNodes
        UNWIND baseNodes as baseNode
        OPTIONAL MATCH (baseNode)-[r:LINKS_TO]->(m:Segment)
        RETURN baseNode as n, r, m
        """

        query = f"""
        MATCH (n:Segment)
        WHERE n.pos >= $start AND n.pos <= $end AND n.chrom = $chrom
        OPTIONAL MATCH (n)-[r:LINKS_TO]->(m:Segment)
        RETURN n, r, m
        """
        parameters = {"start": start, "end": end, "chrom": chrom}
        results = session.run(query, parameters)

        nodeIds = dict()
        nodes = []
        relationships = []
        for result in results:
            n = result["n"]
            r = result["r"]
            m = result["m"]

            if n["id"] not in nodeIds:
                node = {k: n[k] for k in n.keys()}
                nodes.append(node)
            if m["id"] not in nodeIds:
                node = {k: m[k] for k in m.keys()}
                nodes.append(node)

            relationship = {k: r[k] for k in r.keys()}
            relationships.append(relationship)
        
        data = {"nodes": nodes, "links": relationships}


    json_data = json.dumps(data)
    return json_data

#TODO: change to length query directly
def get_lengths_by_id(node_ids):
    with get_session() as session:

        query = """
        UNWIND $ids AS id
        MATCH (n:Segment)
        WHERE n.id = id
        RETURN id, n.sequence AS seq
        """
        parameters = {'ids': node_ids}
        results = session.run(query, parameters)

        lengths = {result['id']: len(result['seq']) for result in results}
        return lengths

def get_annotation_range(chrom, start, end):
    annotations = []
    with get_session() as session:

        query = """
                MATCH (a:Annotation)
                WHERE a.start <= $end AND a.end >= $start AND a.chrom = $chrom
                RETURN a
                """
        parameters = {"start": start, "end": end, "chrom": chrom}
        results = session.run(query, parameters)

        for result in results:
            r = result["a"]
            annotation = {k: r[k] for k in r.keys()}
            annotation["aid"] = r.id

            annotations.append(annotation)

    print("nann", len(annotations))
    return annotations