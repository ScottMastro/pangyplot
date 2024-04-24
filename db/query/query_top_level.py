from db.neo4j_db import get_session
import db.utils.create_record as record
import db.utils.integrity_check as integrity


def get_top_level_data(db, session, genome, chrom, start, end):
    nodes,links = [],[]

    query = """
            MATCH (n:Segment|Chain|Bubble)
            WHERE n.db = $db AND n.genome = $genome AND n.chrom = $chrom 
                AND n.start <= $end AND n.end >= $start AND NOT EXISTS {
                    MATCH (n)-[:INSIDE]->(m)
                    WHERE m.chrom = $chrom AND m.start <= $end AND m.end >= $start
            }
            OPTIONAL MATCH (n)-[r1:END]-(e:Segment)
            OPTIONAL MATCH (n:Segment)-[r2:LINKS_TO]-(s:Segment)

            RETURN n, labels(n) AS type,
            collect(e) as ends,
            collect(DISTINCT r1) AS endlinks,
            collect(DISTINCT r2) AS links
            """
    parameters = {"start": start, "end": end, "db": db, "genome": genome, "chrom": chrom}
    results = session.run(query, parameters)

    ends = []

    for result in results:
        nodes.append( record.node_record(result["n"], result["type"][0]) )

        ends.extend([record.segment_record(r) for r in result["ends"]])

        links.extend( [record.link_record_simple(r) for r in result["endlinks"]] )
        links.extend( [record.link_record_simple(r) for r in result["links"]] )

    for e in ends:
        if ("start" in e and e["start"] > end) or ("end" in e and e["end"] < start):
            continue

        '''query = """
        MATCH (n:Segment)
        WHERE n.id = $id
        MATCH (n)-[r:END]-(m)
        WHERE NOT EXISTS {
            MATCH (m)-[:INSIDE]->(l)-[END]-(n)
        }

        RETURN n, r, m, labels(m) AS type
        """
        '''
        
        query = """
                MATCH (n:Segment)
                WHERE n.id = $id
                MATCH (n)-[l:LINKS_TO]-(m)-[r:END]-(a)
                WHERE m.start IS NULL AND NOT EXISTS {
                    MATCH (a)-[:INSIDE]->(a2)-[END]-(m)
                }

                RETURN m, l, r, a, labels(a) AS type
                """
        parameters = {"id": e["id"]}
        results = session.run(query, parameters)

        print("--------", e["id"])

        for result in results:
            print(record.node_record(result["a"], result["type"][0]) )
            nodes.append( record.node_record(result["a"], result["type"][0]) )
            nodes.append( record.segment_record(result["m"]) )
            link = record.link_record_simple(result["r"])
            print(link)
            links.append( link )
            #links.extend( [record.link_record_simple(r) for r in result["l"]] )



    return nodes, links

def get_top_level(genome, chrom, start, end):

    with get_session() as (db, session):
        nodes,links = get_top_level_data(db, session, genome, chrom, start, end)
        print(len(nodes))

        #segments,segmentLinks = get_top_level_segments(db, session, genome, chrom, start, end)

    #nodes = aggregates + segments
    #links = aggregateLinks + segmentLinks

    nodes = integrity.deduplicate_nodes(nodes)
    links = integrity.deduplicate_links(links)
    links = integrity.remove_invalid_links(nodes, links)

    print(f"TOP LEVEL QUERY: {chrom}:{start}-{end}")
    print(f"   Nodes:{len(nodes)}")
    print(f"   Links:{len(links)}")
    
    graph = {"nodes": nodes, "links": links}

    return graph