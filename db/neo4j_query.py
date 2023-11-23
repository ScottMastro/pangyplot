from neo4j import GraphDatabase
import os
import json
from dotenv import load_dotenv

uri = "neo4j://localhost:7687"
username = "neo4j"
password = "password"  # Replace with the password you set

def db_init():
    load_dotenv()
    #db_user = os.getenv("DB_USER")

def get_bubble_subgraph(id):
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:

        query = """
            MATCH (s:Segment)-[r1:INSIDE]->(b:Bubble)
            WHERE b.id = $i
            MATCH (s)-[r:LINKS_TO]-(s2:Segment)
            RETURN s, collect(r) AS links
            """
        parameters = {"i": id}
        result = session.run(query, parameters)

        segments = []
        links = []

        for record in result:
            for r in record["links"]:
                link = {"source": r.start_node.id,
                        "target": r.end_node.id}
                links.append(link)
            r = record["s"]
            segment = {k: r[k] for k in r.keys()}
            segment["nodeid"] = r.id
            segments.append(segment)
    print("nsegs", len(segments))
    driver.close()
    return segments, links
    

def get_top_level_chains(chrom, start, end):
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:

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
        result = session.run(query, parameters)

        chains = []
        links = []

        for record in result:
            for r in record["ends"]:
                link = {"source": r.start_node.id,
                        "target": r.end_node.id}
                links.append(link)
            r = record["c"]
            chain = {k: r[k] for k in r.keys()}
            # NOTE: r.id is the neo4j node id and r["id"] is the chain id
            chain["nodeid"] = r.id
            chains.append(chain)
    print("nchains", len(chains))
    driver.close()
    return chains, links
    
def get_top_level_bubbles(chrom, start, end):
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:

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
        result = session.run(query, parameters)

        bubbles = []
        links = []

        for record in result:
            for r in record["ends"]:
                link = {"source": r.start_node.id,
                        "target": r.end_node.id}
                links.append(link)
            r = record["b"]
            bubble = {k: r[k] for k in r.keys()}
            # NOTE: r.id is the neo4j node id and r["id"] is the bubble id
            bubble["nodeid"] = r.id
            bubbles.append(bubble)

    print("nbubs", len(bubbles))
    driver.close()
    return bubbles,links

def get_top_level_segments(chrom, start, end):
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:

        # NOTE: we find all segments that overlap the range, but only look for bubbles fully contained
        query = """
                MATCH (s:Segment)
                WHERE s.start <= $end AND s.end >= $start AND s.chrom = $chrom AND NOT EXISTS {
                    MATCH (s)-[:INSIDE]->(n)
                    WHERE n.start >= $start AND n.end <= $end AND n.chrom = $chrom
                }
                MATCH (s)-[r:LINKS_TO]-(m:Segment) 
                RETURN s, collect(r) AS links
                """
        parameters = {"start": start, "end": end, "chrom": chrom}
        result = session.run(query, parameters)

        segments = []
        links = []
        for record in result:
            for r in record["links"]:
                link = {"source": r.start_node.id,
                        "target": r.end_node.id}
                links.append(link)
            r = record["s"]
            segment = {k: r[k] for k in r.keys()}
            # NOTE: r.id is the neo4j node id and r["id"] is the gfa id
            segment["nodeid"] = r.id
            segments.append(segment)

    driver.close()

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

    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:

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
        result = session.run(query, parameters)

        nodeIds = dict()
        nodes = []
        relationships = []
        for record in result:
            n = record["n"]
            r = record["r"]
            m = record["m"]

            if n["id"] not in nodeIds:
                node = {k: n[k] for k in n.keys()}
                nodes.append(node)
            if m["id"] not in nodeIds:
                node = {k: m[k] for k in m.keys()}
                nodes.append(node)

            relationship = {k: r[k] for k in r.keys()}
            relationships.append(relationship)
        
        data = {"nodes": nodes, "links": relationships}

    driver.close()

    json_data = json.dumps(data)
    return json_data

#TODO: change to length query directly
def get_lengths_by_id(node_ids):
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:

        query = """
        UNWIND $ids AS id
        MATCH (n:Segment)
        WHERE n.id = id
        RETURN id, n.sequence AS seq
        """
        parameters = {'ids': node_ids}
        result = session.run(query, parameters)

        lengths = {record['id']: len(record['seq']) for record in result}
        return lengths