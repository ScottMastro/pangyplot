from db.neo4j_db import get_session

def drop_all():

    def delete_in_batches(tx, batch_size):
        query = (
            "MATCH (n) "
            "WITH n LIMIT $batchSize "
            "DETACH DELETE n "
            "RETURN count(n) as deletedCount"
        )
        result = tx.run(query, batchSize=batch_size)
        return result.single()[0]

    with get_session() as session:
        total_deleted = 0
        while True:
            deleted = session.write_transaction(delete_in_batches, batch_size=10000)
            if deleted == 0:
                break
            total_deleted += deleted
            print(f"Deleted {total_deleted} nodes so far...")
        print("Deletion complete.")


def drop_node_type(session, type):

    def delete(tx, batch_size):
        query = f"""
            MATCH (n:{type})
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


def drop_bubbles():
    with get_session() as session:
        drop_node_type(session, "Bubble")
        drop_node_type(session, "Chain")

    print("Deletion complete.")


def drop_annotations():
    types =["Annotation", "Gene", "Transcript", "Exon", "CDS", "Codon", "UTR"]

    with get_session() as session:
        for type in types:
            drop_node_type(session, type)
