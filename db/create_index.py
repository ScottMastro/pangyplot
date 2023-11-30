from neo4j import exceptions

def create_index(session, type, property):
    try:
        session.run(f"CREATE INDEX FOR (n:{type}) ON (n.{property})")
    except exceptions.ClientError as e:
        if "EquivalentSchemaRuleAlreadyExists" in e.code:
            #print("Index already exists.")
            pass
        else:
            raise

def create_restraint(session, type, property):
    try:
        session.run(f"CREATE CONSTRAINT FOR (n:{type}) REQUIRE n.{property} IS UNIQUE")
    except exceptions.ClientError as e:
        if "EquivalentSchemaRuleAlreadyExists" in e.code:
            #print("Constraint already exists.")
            pass
        else:
            raise