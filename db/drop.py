from db.db import get_session

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

def drop_bubbles():
    with get_session() as session:

        def delete_bubbles(tx, batch_size):
            query = (
                "MATCH (n:Bubble) "
                "WITH n LIMIT $batchSize "
                "DETACH DELETE n "
                "RETURN count(n) as deletedCount"
            )
            result = tx.run(query, batchSize=batch_size)
            return result.single()[0]

        total_deleted = 0
        while True:
            deleted = session.write_transaction(delete_bubbles, batch_size=10000)
            if deleted == 0:
                break
            total_deleted += deleted
            print(f"Deleted {total_deleted} bubbles so far...")

        def delete_chains(tx, batch_size):
            query = (
                "MATCH (n:Chain) "
                "WITH n LIMIT $batchSize "
                "DETACH DELETE n "
                "RETURN count(n) as deletedCount"
            )
            result = tx.run(query, batchSize=batch_size)
            return result.single()[0]

        total_deleted = 0
        while True:
            deleted = session.write_transaction(delete_chains, batch_size=10000)
            if deleted == 0:
                break
            total_deleted += deleted
            print(f"Deleted {total_deleted} bubbles so far...")

        print("Deletion complete.")

def drop_annotations():
    with get_session() as session:

        def delete(tx, batch_size):
            query = (
                "MATCH (n:Annotation) "
                "WITH n LIMIT $batchSize "
                "DETACH DELETE n "
                "RETURN count(n) as deletedCount"
            )
            result = tx.run(query, batchSize=batch_size)
            return result.single()[0]

        total_deleted = 0
        while True:
            deleted = session.write_transaction(delete, batch_size=10000)
            if deleted == 0:
                break
            total_deleted += deleted
            print(f"Deleted {total_deleted} annotations so far...")
        print("Deletion complete.")