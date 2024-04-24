from db.neo4j_db import get_session

def drop_all():
   
   with get_session() as (_, session):

        def delete_in_batches(tx, batch_size):
            query = f"""
                MATCH (n)
                WITH n LIMIT $batchSize
                DETACH DELETE n
                RETURN count(n) as deletedCount"""
            
            result = tx.run(query, batchSize=batch_size)
            return result.single()[0]

        total_deleted = 0
        while True:
            deleted = session.write_transaction(delete_in_batches, batch_size=10000)
            if deleted == 0:
                break
            total_deleted += deleted
            print(f"Deleted {total_deleted} nodes so far...")
        print("Deletion complete.")

def drop_db(db):
   
   with get_session() as (_, session):

        def delete_in_batches(tx, batch_size):
            query = f"""
                MATCH (n) WHERE n.db = "{db}"
                WITH n LIMIT $batchSize
                DETACH DELETE n
                RETURN count(n) as deletedCount"""
            
            result = tx.run(query, batchSize=batch_size)
            return result.single()[0]

        total_deleted = 0
        while True:
            deleted = session.write_transaction(delete_in_batches, batch_size=10000)
            if deleted == 0:
                break
            total_deleted += deleted
            print(f"Deleted {total_deleted} nodes so far...")
        print("Deletion complete.")

def drop_node_type(session, type, db=None):

    db_clause = f'WHERE n.db = "{db}"' if db else ''

    def delete(tx, batch_size):
        query = f"""
            MATCH (n:{type}) {db_clause}
            WITH n LIMIT $batchSize
            DETACH DELETE n
            RETURN count(n) as deletedCount"""
        result = tx.run(query, batchSize=batch_size)
        return result.single()[0]

    total_deleted = 0
    while True:
        deleted = session.write_transaction(delete, batch_size=10000)
        if deleted == 0:
            break
        total_deleted += deleted
        print(f"Deleted {total_deleted} {type} so far...")

def drop_relationship_type(session, type, db=None):

    db_clause = f'WHERE x.db = "{db}"' if db else ''

    def delete(tx, batch_size):
        query = f"""
            MATCH (x)-[r:{type}]-() {db_clause}
            WITH r LIMIT $batchSize
            DELETE r
            RETURN count(r) as deletedCount"""
        result = tx.run(query, batchSize=batch_size)
        return result.single()[0]

    total_deleted = 0
    while True:
        deleted = session.write_transaction(delete, batch_size=10000)
        if deleted == 0:
            break
        total_deleted += deleted
        print(f"Deleted {total_deleted} {type} relationships so far...")

def drop_bubbles():
    with get_session() as (db, session):
        drop_node_type(session, "Bubble", db)
        drop_node_type(session, "Chain", db)

    print("Deletion complete.")


def drop_subgraphs():
    with get_session() as (db, session):
        drop_node_type(session, "Subgraph", db)
    
def drop_anchors():
    with get_session() as (db, session):
        drop_relationship_type(session, "ANCHOR", db)

def drop_annotations():
    types =["Annotation", "Gene", "Transcript", "Exon", "CDS", "Codon", "UTR"]

    with get_session() as (_, session):
        for type in types:
            drop_node_type(session, type)
