from db.neo4j_db import get_session
import db.utils.create_record as record
from BubbleGun.compact_graph import merge_start,merge_end

def get_all_segments(db, session, segments):
    query = """
            UNWIND $segment_ids AS segment_id
            MATCH (n:Segment {db: $db, id: segment_id})
            RETURN n
            """
    nodes_result = session.run(query, {"db": db, "segment_ids": segments})
    nodes = [record.segment_record(result["n"]) for result in nodes_result]
    return nodes


def combine_node_properties(nodes, mainId):
    combinedNode = None
    for node in nodes:
        if node["id"] == mainId:
            combinedNode = node

    combinedNode["compact"] = [n["id"] for n in nodes]
    #todo: might have to adjust for reverse compliment and correct order
    combinedNode["sequence"] = "".join([n["sequence"] for n in nodes])
    combinedNode["length"] = len(combinedNode["sequence"])
    combinedNode["gcCount"] = combinedNode["sequence"].count('G') + combinedNode["sequence"].count('C') + combinedNode["sequence"].count('g') + combinedNode["sequence"].count('c')
    combinedNode["start"] = min([n["start"] for n in nodes if n["start"] is not None], default=None)
    combinedNode["end"] = max([n["end"] for n in nodes if n["end"] is not None], default=None)

    xDir = sum([1 if n["x1"] < n["x2"] else -1 for n in nodes])
    yDir = sum([1 if n["y1"] < n["y2"] else -1 for n in nodes])

    headX = (nodes[0]["x1"] + nodes[0]["x2"])/2
    headY = (nodes[0]["y1"] + nodes[0]["y2"])/2
    tailX = (nodes[-1]["x1"] + nodes[-1]["x2"])/2
    tailY = (nodes[-1]["y1"] + nodes[-1]["y2"])/2

    if xDir >= 0:
        combinedNode["x1"] = min(headX, tailX) 
        combinedNode["x2"] = max(headX, tailX) 
    else:
        combinedNode["x1"] = max(headX, tailX) 
        combinedNode["x2"] = min(headX, tailX)

    if yDir >= 0:
        combinedNode["y1"] = min(headY, tailY) 
        combinedNode["y2"] = max(headY, tailY) 
    else:
        combinedNode["y1"] = max(headY, tailY) 
        combinedNode["y2"] = min(headY, tailY) 
    return combinedNode

def get_outside_links(db, session, segments):
        
    headId = segments[0]
    tailId = segments[-1]

    query = """
        MATCH (a:Segment)-[r:LINKS_TO]->(head:Segment)
        WHERE head.db = $db AND head.id = $head_id
        RETURN a.id AS other_id, head.id AS node_id, r, 'incoming' AS direction
        UNION
        MATCH (head:Segment)-[r:LINKS_TO]->(a:Segment)
        WHERE head.db = $db AND head.id = $head_id
        RETURN a.id AS other_id, head.id AS node_id, r, 'outgoing' AS direction
        UNION
        MATCH (tail:Segment)-[r:LINKS_TO]->(b:Segment)
        WHERE tail.db = $db AND tail.id = $tail_id
        RETURN b.id AS other_id, tail.id AS node_id, r, 'outgoing' AS direction
        UNION
        MATCH (b:Segment)-[r:LINKS_TO]->(tail:Segment)
        WHERE tail.db = $db AND tail.id = $tail_id
        RETURN b.id AS other_id, tail.id AS node_id, r, 'incoming' AS direction
    """

    results = session.run(query, {"db": db, "head_id": headId, "tail_id": tailId})

    incomingLinks = []
    outgoingLinks = []

    for result in results:
        other_id = result["other_id"]
        direction = result["direction"]

        if other_id in segments:
            continue

        link = record.link_record(result["r"])

        if direction == "incoming":
            link["from_id"] = other_id
            link["to_id"] = result["node_id"]
            incomingLinks.append(link)

        elif direction == "outgoing":
            link["from_id"] = result["node_id"]
            link["to_id"] = other_id 
            outgoingLinks.append(link)

    return incomingLinks, outgoingLinks

def add_combined_segment(db, session, combinedNode):
    # todo: use the same function as insert_segment.py
    query = """
            UNWIND $segments AS segment
            CREATE (:Segment {
                id: segment.id,
                db: $db,
                genome: segment.genome,
                chrom: segment.chrom,
                start: segment.start,
                end: segment.end,
                x1: segment.x1,
                y1: segment.y1,
                y2: segment.y2,
                x2: segment.x2,
                length: segment.length,
                sequence: segment.sequence,
                gcCount: segment.gcCount,
                isRef: segment.isRef,
                compact: segment.compact
            })
            """
    session.run(query, {"db":db, "segments": [combinedNode]})

def drop_by_ids(db, session, segments):

    query = """
            MATCH (s:Segment)
            WHERE s.db = $db AND s.id IN $segment_ids
            DETACH DELETE s       
            """
    session.run(query, {"db": db, "segment_ids": segments})

def reconnect_outside_links(db, session, combinedNode, incomingLinks, outgoingLinks):
    combinedNodeId = combinedNode["id"]

    # Reconnect incoming links
    query = """
    UNWIND $links AS link
    MATCH (a:Segment {db: $db, id: link.from_id}), (new:Segment {db: $db, id: $to_id})
    CREATE (a)-[r:LINKS_TO {
        from_strand: link.from_strand,
        to_strand: link.to_strand,
        haplotype: link.haplotype,
        frequency: link.frequency,
        isRef: link.is_ref
    }]->(new)
    """
    session.run(query, {"db": db, 
                        "to_id": combinedNodeId,
                        "links": incomingLinks})

    # Reconnect outgoing links
    query = """
    UNWIND $links AS link
    MATCH (new:Segment {db: $db, id: $from_id}), (b:Segment {db: $db, id: link.to_id})
    CREATE (new)-[r:LINKS_TO {
        from_strand: link.from_strand,
        to_strand: link.to_strand,
        haplotype: link.haplotype,
        frequency: link.frequency,
        isRef: link.is_ref
    }]->(b)
    """
    session.run(query, {
        "db": db,
        "from_id": combinedNodeId,
        "links": outgoingLinks
    })


def compact_segment(segments, mainId):

    with get_session() as (db, session):
        
        # Step 1: Fetch all nodes in the cluster by their IDs
        nodes = get_all_segments(db, session, segments)

        # Step 2: Combine properties of all nodes
        combinedNode = combine_node_properties(nodes, mainId)

        # Step 3: Get all incoming and outgoing links for the head and tail
        incomingLinks, outgoingLinks = get_outside_links(db, session, segments)

        # Step 4: Remove all nodes in the cluster
        drop_by_ids(db, session, segments)

        # Step 5: Create a new combined node
        add_combined_segment(db, session, combinedNode)

        # Step 6: Reconnect the incoming and outgoing links
        reconnect_outside_links(db, session, combinedNode, incomingLinks, outgoingLinks)




def compact_graph(graph):
    count = 0
    nodes = list(graph.nodes.keys())
    for n in nodes:
        cluster = []

        if n in graph.nodes:
            while True:
                if len(graph.nodes[n].end) == 1: 
                    other = graph.nodes[n].end[0][0]
                    merge = merge_end(graph, n)
                    if merge:
                        cluster.append(other)
                        continue
                break

            cluster.reverse()
            cluster.append(n)

            while True:
                if len(graph.nodes[n].start) == 1:
                    other = graph.nodes[n].start[0][0]
                    merge = merge_start(graph, n)
                    if merge:
                        cluster.append(other)
                        continue
                break

            cluster.reverse()
            
            if len(cluster) > 1:
                count+=1
                if count % 1000 == 0:
                    print(".", end='', flush=True)
                compact_segment(cluster, n)

