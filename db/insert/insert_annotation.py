from db.neo4j_db import get_session

GENE="Gene"

def add_annotations_by_type(session, annotations, type, batchSize):
    if len(annotations) == 0: return
    for i in range(0, len(annotations), batchSize):
        batch = annotations[i:i + batchSize]
        query = f"""
                UNWIND $batch AS ann
                CREATE (a:{type})
                SET a += ann
                """
        session.run(query, {"batch": batch})

def add_gene_links(session):
    query = (
        "MATCH (n) WHERE n.gene_id IS NOT NULL "
        "MATCH (g:Gene) WHERE g.id = n.gene_id "
        "MERGE (n)-[:GENE]->(g)"
    )
    session.run(query)

def add_annotation_links(session):

    query = """
            MATCH (t:Transcript) WHERE t.gene_id IS NOT NULL
            MATCH (g:Gene) WHERE g.id = t.gene_id
            MERGE (t)-[:INSIDE]->(g)
            """
    session.run(query)
                
    query = """
            MATCH (n) WHERE n.transcript_id IS NOT NULL
            MATCH (t:Transcript) WHERE t.id = n.transcript_id
            MERGE (n)-[:INSIDE]->(t)
            """
    session.run(query)

def add_annotations(annotationDict, batchSize=10000):   

    with get_session() as session:

        add_annotations_by_type(session, annotationDict[GENE], GENE, batchSize)
        print(GENE, len(annotationDict[GENE]))
        del annotationDict[GENE]

        for type in annotationDict:
            print(type, len(annotationDict[type]))
            add_annotations_by_type(session, annotationDict[type], type, batchSize)
        
        add_annotation_links(session)
