from neo4j import GraphDatabase
import json

uri = "neo4j://localhost:7687"
username = "neo4j"
password = "password"  # Replace with the password you set

def get_segments(chrom, start, end):
    data = []

    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:

        query = f"""
        MATCH (n:Segment)
        WHERE n.id >= {start} AND n.id <= {end} AND n.chrom = "{chrom}"
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