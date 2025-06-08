from db.neo4j_db import get_session
from db.query.query_all import query_all_db

def get_status():
   
    dbs = query_all_db()

    with get_session() as (_, session):
        for db in dbs:
            print(F"DB: {db}\n-----------------")

            nodes_query = f'MATCH (n) WHERE n.db = "{db}" RETURN labels(n) AS labels, COUNT(n) AS count'
            nodes_result = session.run(nodes_query)
            
            edges_query = f'MATCH (n)-[r]->(m) WHERE n.db = "{db}" RETURN type(r) AS type, COUNT(r) AS count'
            edges_result = session.run(edges_query)
            
            print("Nodes count by label:")
            for record in nodes_result:
                print(f"{record['labels'][0]}s: {record['count']}")
            
            print("\nRelationships count by type:")
            for record in edges_result:
                print(f"Type {record['type']}: {record['count']}")
        
            print(f"-----------------")

        nodes_query = f'MATCH (n) WHERE n.db IS NULL RETURN labels(n) AS labels, COUNT(n) AS count'
        nodes_result = session.run(nodes_query)
        
        print("Annotations:")
        for record in nodes_result:
            print(f"{record['labels'][0]}s: {record['count']}")
        


