import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
import db.utils.create_index as index

NEO4J_DRIVER = None
GENE_TEXT_INDEX = "gene_fulltext_index"
CURRENT_DB = "neo4j"

def create_database(db_name):
    with NEO4J_DRIVER.session() as session:
        result = session.run("SHOW DATABASES")
        existing_dbs = [record["name"] for record in result]
        if db_name not in existing_dbs:
            session.run(f"CREATE DATABASE {db_name}")
            print(f"Database {db_name} created.")
        else:
            print(f"Database {db_name} already exists.")

def init_driver(db_name):
    load_dotenv()
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")

    global NEO4J_DRIVER
    uri = f"neo4j://{db_host}:{db_port}"
    NEO4J_DRIVER = GraphDatabase.driver(uri, auth=(db_user, db_pass))
    if db_name is not None:
        CURRENT_DB = db_name
    create_database(db_name)

def get_session():
    if NEO4J_DRIVER is None:
        raise Exception("Neo4j driver is not initialized.")
    return NEO4J_DRIVER.session(database=CURRENT_DB)

def close_driver():
    if NEO4J_DRIVER is not None:
        NEO4J_DRIVER.close()



def db_init(db_name=None):
    init_driver(db_name)

    with get_session() as session:

        #index.drop_all_index(session)
        compoundPosition = ["chrom", "start", "end"]

        for x in ["Segment", "Bubble", "Chain"]:
            index.create_restraint(session, x, "id")
            index.create_index(session, x, compoundPosition)

        index.create_index(session, "Annotation", compoundPosition)
        index.create_index(session, "Gene", compoundPosition)

        index.create_restraint(session, "Gene", "id")
        index.create_restraint(session, "Transcript", "id")
        index.create_restraint(session, "Exon", "id")

        index.create_fulltext_node_index(session, "Gene", GENE_TEXT_INDEX, ["gene", "id"])