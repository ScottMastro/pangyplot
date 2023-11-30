import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
from db.create_index import create_restraint, create_compound_index, drop_all_index

NEO4J_DRIVER = None

def init_driver():
    load_dotenv()
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")

    global NEO4J_DRIVER
    uri = f"{db_name}://{db_host}:{db_port}"
    NEO4J_DRIVER = GraphDatabase.driver(uri, auth=(db_user, db_pass))

def get_session():
    if NEO4J_DRIVER is None:
        raise Exception("Neo4j driver is not initialized.")
    return NEO4J_DRIVER.session()

def close_driver():
    if NEO4J_DRIVER is not None:
        NEO4J_DRIVER.close()

def db_init():
    init_driver()

    with get_session() as session:

        #drop_all_index(session)
        compoundPosition = ["chrom", "start", "end"]

        for x in ["Segment", "Bubble", "Chain"]:
            create_restraint(session, x, "id")
            create_compound_index(session, x, compoundPosition)

        create_compound_index(session, "Annotation", compoundPosition)