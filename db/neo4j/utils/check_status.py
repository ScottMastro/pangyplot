from db.neo4j.neo4j_db import get_session, db_init

from db.query.query_all import query_all_db
from db.query.query_all import query_all_genome

def format_datetime(dt):
    dt_str = "N/A"
    if dt:
        try:
            dt_str = dt.to_native().strftime("%b %d, %Y %H:%M")
        except Exception:
            dt_str = str(dt)
    else:
        dt_str = "N/A"
    return dt_str

def get_status():
    db_init(None)
    dash="-----------------"

    with get_session() as (_, session):

        for db in query_all_db():
            print(f"{dash}\ndb: {db}\n{dash}")

            for t in ["Sample", "Segment", "Bubble", "Chain"]:
                q = f'MATCH (n:{t}) WHERE n.db = $db RETURN COUNT(n) AS count'
                r = session.run(q, {"db": db})
                count = r.single()["count"]
                print(f"🔹 {t}s: {count}")


            q = f"MATCH (c:Collection) WHERE c.db = $db RETURN c"
            r = session.run(q, {"db": db})

            for record in r:
                node = record["c"]
                props = dict(node)

                cid = props.get("id", "N/A")
                genome = props.get("genome", "N/A")
                dt = format_datetime(props.get("datetime"))

                file = props.get("file", "N/A")

                print(f"\n  collection: {cid} (genome={genome})")
                print(f"  🔸 Uploaded: {dt}")
                print(f"  🔸 Source: {file}")
        
            print("")

        print(f"{dash}{dash}")
        print("ANNOTATIONS\n")
        
        for genome in query_all_genome(all_dbs=True):

            print(f"{dash}\ngenome: {genome}\n{dash}")

            for t in ["Gene", "Transcript", "Exon"]:
                q = f'MATCH (n:{t}) WHERE n.genome = $genome RETURN COUNT(n) AS count'
                r = session.run(q, {"genome": genome})
                count = r.single()["count"]
                print(f"🔹 {t}s: {count}")


        


