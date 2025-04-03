import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
from contextlib import contextmanager
import db.utils.create_index as index


NEO4J_DRIVER = None
GENE_TEXT_INDEX = "gene_fulltext_index"
CURRENT_DB = None

def init_driver():
    load_dotenv()
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")

    global NEO4J_DRIVER
    global CURRENT_DB
    uri = f"{db_host}:{db_port}"
    NEO4J_DRIVER = GraphDatabase.driver(uri, auth=(db_user, db_pass))

def update_db(dbName):
    global CURRENT_DB
    if dbName is not None:
        CURRENT_DB = dbName
    else:
        CURRENT_DB = "default"

def get_session_old():
    if NEO4J_DRIVER is None:
        raise Exception("Neo4j driver is not initialized.")
    db = CURRENT_DB
    return db, NEO4J_DRIVER.session()

@contextmanager
def get_session():
    if NEO4J_DRIVER is None:
        raise Exception("Neo4j driver is not initialized.")
    db = CURRENT_DB
    session_cm = NEO4J_DRIVER.session()
    try:
        yield db, session_cm.__enter__()
    finally:
        session_cm.__exit__(None, None, None)

def create_dummy_relationship(session, type):
    query = """
    MERGE (a:Dummy {id: 'dummy_start'})
    MERGE (b:Dummy {id: 'dummy_end'})
    MERGE (a)-[:"""+type+"""]->(b)
    """
    session.run(query)

def close_driver():
    if NEO4J_DRIVER is not None:
        NEO4J_DRIVER.close()

def db_init(dbName=None):
    init_driver()
    update_db(dbName)
    
    with get_session() as (db, session):

        #index.drop_all_constraints(session)
        #index.drop_all_index(session)

        create_dummy_relationship(session, "ANCHOR") 
               
        compoundPosition = ["db", "genome", "chrom", "start", "end"]

        for x in ["Segment", "Bubble", "Chain"]:
            index.create_restraint(session, x, ["db","id"])
            index.create_index(session, x, compoundPosition)

        index.create_restraint(session, "Subgraph", ["db","id"])

        compoundPosition = ["genome", "chrom", "start", "end"]

        index.create_index(session, "Annotation", compoundPosition)
        index.create_index(session, "Gene", compoundPosition)

        index.create_restraint(session, "Gene", "id")
        index.create_restraint(session, "Transcript", "id")
        index.create_restraint(session, "Exon", "id")

        index.create_fulltext_node_index(session, "Gene", GENE_TEXT_INDEX, ["gene", "id"])