from neo4j import exceptions

def create_index(session, type, properties):
    try:
        properties_str = ", ".join(f"n.{prop}" for prop in properties)
        session.run(f"CREATE INDEX FOR (n:{type}) ON ({properties_str})")
    except exceptions.ClientError as e:
        if "EquivalentSchemaRuleAlreadyExists" in e.code:
            # Index already exists.
            pass
        else:
            raise

def create_restraint(session, type, property):
    try:
        session.run(f"CREATE CONSTRAINT FOR (n:{type}) REQUIRE n.{property} IS UNIQUE")
    except exceptions.ClientError as e:
        if "EquivalentSchemaRuleAlreadyExists" in e.code:
            # Index already exists.
            pass
        else:
            raise

def drop_index(session, index_name):
    session.run(f"DROP INDEX {index_name}")

def drop_all_index(session):
    indexes = session.run("SHOW INDEXES")
    for index in indexes:
        try:
            index_name = index["name"]
            session.run(f"DROP INDEX {index_name}")
            print(f"Index {index_name} dropped.")
        except exceptions.ClientError as e:
            print(f"Failed to drop index {index_name}: {e}")

def print_all_index(session):
    result = session.run("SHOW INDEXES")
    for record in result:
        print(record["name"], record["labelsOrTypes"], record["properties"], record["state"])