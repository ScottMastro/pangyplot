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

def add_annotation_links(genome, session):

    query = """
            MATCH (t:Transcript) WHERE t.gene_id IS NOT NULL AND t.genome = $genome
            MATCH (g:Gene) WHERE g.id = t.gene_id AND g.genome = $genome
            MERGE (t)-[:INSIDE]->(g)
            """
    session.run(query, parameters={'genome': genome})
                
    query = """
            MATCH (n) WHERE n.transcript_id IS NOT NULL AND n.genome = $genome
            MATCH (t:Transcript) WHERE t.id = n.transcript_id AND t.genome = $genome
            MERGE (n)-[:INSIDE]->(t)
            """
    session.run(query, parameters={'genome': genome})
    
def add_annotations(refGenome, annotationDict, batchSize=10000):

    with get_session() as (db, session):

        add_annotations_by_type(session, annotationDict[GENE], GENE, batchSize)
        print(GENE, len(annotationDict[GENE]))
        del annotationDict[GENE]

        for type in annotationDict:
            print(type, len(annotationDict[type]))
            add_annotations_by_type(session, annotationDict[type], type, batchSize)
        
        add_annotation_links(refGenome, session)
