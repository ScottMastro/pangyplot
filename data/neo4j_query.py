from neo4j import GraphDatabase,exceptions
import time

uri = "neo4j://localhost:7687"
username = "neo4j"
password = "password"  # Replace with the password you set

def get_segments(chrom, start, end):
    
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:

        '''
        MATCH (n:Segment)
        WHERE n.id >= "36923624" AND n.id <= "36924829"
        WITH collect(n) as baseNodes
        UNWIND baseNodes as baseNode
        OPTIONAL MATCH (baseNode)-[r:LINKS_TO]->(m:Segment)
        RETURN baseNode as n, r, m
        '''

        query = """
        MATCH (n:Segment)
        WHERE n.id >= "36923624" AND n.id <= "36924829"
        OPTIONAL MATCH (n)-[r:LINKS_TO]->(m:Segment)
        RETURN n, r, m
        """
        result = session.run(query)


        for record in result:
            n = record['n']
            r = record['r']
            m = record['m']
            print(f"Node: {n}, Relationship: {r}, Connected Node: {m}")

    driver.close()

    return(result)


def get_segments(chrom, start, end):
    
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:

        '''
        MATCH (n:Segment)
        WHERE n.id >= "36923624" AND n.id <= "36924829"
        WITH collect(n) as baseNodes
        UNWIND baseNodes as baseNode
        OPTIONAL MATCH (baseNode)-[r:LINKS_TO]->(m:Segment)
        RETURN baseNode as n, r, m
        '''

        query = """
        MATCH (n:Segment)
        WHERE n.id >= "36923624" AND n.id <= "36924829"
        OPTIONAL MATCH (n)-[r:LINKS_TO]->(m:Segment)
        RETURN n, r, m
        """
        result = session.run(query)


        for record in result:
            n = record['n']
            r = record['r']
            m = record['m']
            print(f"Node: {n}, Relationship: {r}, Connected Node: {m}")
            
    driver.close()

    return(result)

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