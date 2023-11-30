from db.db import get_session
from db.record import segment_record, link_record

def get_segments(session, x, y):

    query = """
            MATCH (s1:Segment)-[:LINKS_TO]-(s2:Segment)
            WHERE s1.id = $x AND s2.id = $y
            RETURN s1, s2
            """

    result = session.run(query, {"x": x, "y": y})

    nodeX, nodeY = None, None
    for record in result:
        nodeX = segment_record(record["s1"])
        nodeY = segment_record(record["s2"])

    return (nodeX,nodeY)

def get_other_links(session, x, y):

    query = """
            MATCH (s1:Segment)-[l:LINKS_TO]-(s2:Segment)
            WHERE s1.id <> $x AND s2.id = $y
            RETURN l
            """
    result = session.run(query, {"x": x, "y": y})

    links = []
    for record in result:
        link = link_record(record["l"])
        links.append(link)

    return links
    
def drop_by_id(session, id):

    query = """
            MATCH (s:Segment)
            WHERE s.id = $id
            DETACH DELETE s       
            """
    session.run(query, {"id": id})

def combine_nodes(session, keepNode, removeNode):
    params = {"id": keepNode["id"]}
    params["compact"] = [] if "compact" not in keepNode else keepNode["compact"]
    params["compact"].append(removeNode["id"])
    params["x2"] = removeNode["x2"]
    params["y2"] = removeNode["y2"]
    params["sequence"] = keepNode["sequence"] + removeNode["sequence"]
    params["length"] = len(params["sequence"])

    query = """
            MATCH (s:Segment { id: $id })
            SET s.compact = $compact,
                s.x2 = $x2,
                s.y2 = $y2,
                s.sequence = $sequence,
                s.length = $length
            """
    session.run(query, params)

def restore_links(session, keepNode, removeNode, recoverLinks):
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
            WHERE ID(a) = link.source AND ID(b) = link.target
            CREATE (a)-[:LINKS_TO {
                from_strand: link.from_strand,
                to_strand: link.to_strand,
                haplotype: link.haplotype,
                frequency: link.frequency}]->(b)
            """
    result = session.run(query, {"links": recoverLinks})
    #summary = result.consume()
    #relationships_created = summary.counters.relationships_created
    #print("relationships_created:", relationships_created)

def compact_segment(keepSegmentId, removeSegmentId):

    with get_session() as session:

        keepNode, removeNode = get_segments(session, keepSegmentId, removeSegmentId)
        recoverLinks = get_other_links(session, keepSegmentId, removeSegmentId)

        #print("keepNode", keepNode)
        #print("removeNode", removeNode)
        #print("recoverLinks", recoverLinks)

        drop_by_id(session, removeSegmentId)
        combine_nodes(session, keepNode, removeNode)
        restore_links(session, keepNode, removeNode, recoverLinks)

