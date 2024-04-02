from db.neo4j_db import get_session
import db.utils.create_record as record

def get_segments(db, session, x, y):

    query = """
            MATCH (s1:Segment)-[:LINKS_TO]-(s2:Segment)
            WHERE s1.db = $db AND s1.id = $x AND s2.id = $y
            RETURN s1, s2
            """

    results = session.run(query, {"x": x, "y": y, "db": db})

    nodeX, nodeY = None, None
    for result in results:
        nodeX = record.segment_record(result["s1"])
        nodeY = record.segment_record(result["s2"])

    return (nodeX,nodeY)

def get_other_links(db, session, x, y):

    query = """
            MATCH (s1:Segment)-[l:LINKS_TO]-(s2:Segment)
            WHERE s1.db = $db AND s1.id <> $x AND s2.id = $y
            RETURN l
            """
    results = session.run(query, {"x": x, "y": y, "db": db})

    links = []
    for result in results:
        link = record.link_record(result["l"])
        links.append(link)

    return links
    
def drop_by_id(db, session, id):

    query = """
            MATCH (s:Segment)
            WHERE s.db = $db AND s.id = $id
            DETACH DELETE s       
            """
    session.run(query, {"id": id, "db": db})

def combine_nodes(db, session, keepNode, removeNode):
    params = {"id": keepNode["id"]}
    params["compact"] = [] if "compact" not in keepNode else keepNode["compact"]
    params["compact"].append(removeNode["id"])
    params["x2"] = removeNode["x2"]
    params["y2"] = removeNode["y2"]
    params["sequence"] = keepNode["sequence"] + removeNode["sequence"]
    params["length"] = len(params["sequence"])
    params["db"] = db

    query = """
            MATCH (s:Segment {db: $db, id: $id })
            SET s.db = $db,
                s.compact = $compact,
                s.x2 = $x2,
                s.y2 = $y2,
                s.sequence = $sequence,
                s.length = $length
            """
    session.run(query, params)

def restore_links(db, session, keepNode, removeNode, recoverLinks):
    keepSegmentNodeId = keepNode["nodeid"]
    removeSegmentNodeId = removeNode["nodeid"]
    for link in recoverLinks:
        if link["source"] == removeSegmentNodeId:
            link["source"] = keepSegmentNodeId
        if link["target"] == removeSegmentNodeId:
            link["target"] = keepSegmentNodeId

    query = """
            UNWIND $links AS link
            MATCH (a:Segment), (b:Segment)
            WHERE a.db = $db AND ID(a) = link.source AND ID(b) = link.target
            CREATE (a)-[:LINKS_TO {
                from_strand: link.from_strand,
                to_strand: link.to_strand,
                haplotype: link.haplotype,
                frequency: link.frequency}]->(b)
            """
    result = session.run(query, {"db": db, "links": recoverLinks})
    #summary = result.consume()
    #relationships_created = summary.counters.relationships_created
    #print("relationships_created:", relationships_created)

def compact_segment(keepSegmentId, removeSegmentId):

    with get_session() as (db, session):
        print(keepSegmentId, removeSegmentId)
        keepNode, removeNode = get_segments(db, session, keepSegmentId, removeSegmentId)
        recoverLinks = get_other_links(db, session, keepSegmentId, removeSegmentId)

        #print("keepNode", keepNode)
        #print("removeNode", removeNode)
        #print("recoverLinks", recoverLinks)

        drop_by_id(db, session, removeSegmentId)
        combine_nodes(db, session, keepNode, removeNode)
        restore_links(db, session, keepNode, removeNode, recoverLinks)

