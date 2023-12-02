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

def get_annotations(chrom, start, end):
    annotations = get_annotation_range(chrom, start, end)
    return annotations

def get_subgraph(nodeid):
    segments,links = get_subgraph(nodeid)
    return {"nodes": segments, "links": links}
