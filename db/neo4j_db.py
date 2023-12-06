import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
import db.utils.create_index as index

NEO4J_DRIVER = None
GENE_TEXT_INDEX = "gene_fulltext_index"

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