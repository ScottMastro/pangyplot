from db.neo4j_db import get_session
import db.utils.create_record as record
import db.utils.integrity_check as integrity

def get_top_level_data(db, session, genome, chrom, start, end):
    nodes,links = [],[]

    bubble_query = """
            MATCH (n:Segment|Bubble)
            WHERE n.db = $db AND n.genome = $genome AND n.chrom = $chrom 
                AND n.start >= $start AND n.end <= $end AND NOT EXISTS {
                    MATCH (n)-[:INSIDE]->(m)
                    WHERE m.chrom = $chrom AND m.start >= $start AND m.end <= $end
            }
            OPTIONAL MATCH (n)-[r1:END]-(e:Segment)
            OPTIONAL MATCH (n:Segment)-[r2:LINKS_TO]-(s:Segment)

            RETURN n, labels(n) AS type,
            collect(DISTINCT r1) AS endlinks,
            collect(DISTINCT r2) AS links
            """
    parameters = {"start": start, "end": end, "db": db, "genome": genome, "chrom": chrom}
    results = session.run(bubble_query, parameters)

    for result in results:
        nodes.append( record.node_record(result["n"], result["type"][0]) )

        links.extend( [record.link_record(r) for r in result["endlinks"]] )
        links.extend( [record.link_record(r) for r in result["links"]] )

    chain_query = """
            MATCH (n:Chain)-[r1:CHAINED]-(b:Bubble)
            WHERE n.db = $db AND n.genome = $genome AND n.chrom = $chrom 
                AND n.start >= $start AND n.end <= $end AND NOT EXISTS {
                    MATCH (n)-[:PARENT_SB]->(m)
                    WHERE m.chrom = $chrom AND m.start >= $start AND m.end <= $end
            }
            OPTIONAL MATCH (n)-[r2:CHAIN_END]-(e:Segment)

            RETURN n, b,
            collect(DISTINCT r1) AS chainlinks,
            collect(DISTINCT r2) AS endlinks
            """
    parameters = {"start": start, "end": end, "db": db, "genome": genome, "chrom": chrom}
    results = session.run(chain_query, parameters)

    for result in results:
        print( record.chain_record(result["n"]) )

        print( [record.link_record(r) for r in result["endlinks"]] )
        print( [record.link_record(r) for r in result["chainlinks"]] )


    alt_query = """
            MATCH (n:Segment)
            WHERE n.db = $db AND n.genome = $genome AND n.chrom = $chrom 
                AND n.start <= $end AND n.end >= $start 
            MATCH (n)<-[:ANCHOR]-(a)
            WHERE NOT EXISTS {
                    MATCH (a)-[:INSIDE*]->(m)
                    WHERE m.start IS NOT NULL
            }
            OPTIONAL MATCH (a)-[r1:END]-(e:Segment)
            OPTIONAL MATCH (a:Segment)-[r2:LINKS_TO]-(s:Segment)

            RETURN a, labels(a) AS type,
            collect(DISTINCT r1) AS endlinks,
            collect(DISTINCT r2) AS links
            """
    parameters = {"start": start, "end": end, "db": db, "genome": genome, "chrom": chrom}
    results = session.run(alt_query, parameters)

    for result in results:
        nodes.append( record.node_record(result["a"], result["type"][0]) )
        links.extend( [record.link_record_simple(r) for r in result["endlinks"]] )
        links.extend( [record.link_record_simple(r) for r in result["links"]] )

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

    print(f"🔎 TOP LEVEL QUERY: {chrom}:{start}-{end}")
    print(f"   Nodes:{len(nodes)}")
    print(f"   Links:{len(links)}")
    
    graph = {"nodes": nodes, "links": links}

    return graph