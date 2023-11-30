from db.db import get_session

def add_annotations(annotations, batch_size=10000):
    if len(annotations) == 0: return
    with get_session() as session:

        for i in range(0, len(annotations), batch_size):
            batch = annotations[i:i + batch_size]
            query = """
                UNWIND $batch AS ann
                CREATE (a:Annotation)
                SET a += ann
            """
            session.run(query, {"batch": batch})


