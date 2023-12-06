from db.neo4j_db import get_session
import db.utils.create_record as record

def create_gene_objects(data):
    
    geneDict = dict()
    transcriptDict = dict()
    types = ["Exon", "CDS", "Codon", "UTR"]
    typeDict = {x:f"_{x.lower()}" for x in types}

    for result in data:
        gene,transcript,type,other = result
        gid = gene["id"]
        tid = transcript["id"]

        if not gid in geneDict:
            gene["_transcripts"] = []
            geneDict[gid] = gene
        gene = geneDict[gid]

        if not tid in transcriptDict:
            for type in typeDict: 
                transcript[typeDict[type]] = []
            gene["_transcripts"].append(transcript)
            transcriptDict[tid] = transcript
        transcript = transcriptDict[tid]

        transcript[typeDict[type]].append(other)

    return [geneDict[gid] for gid in geneDict]


def query_gene_range(chrom, start, end):
    with get_session() as session:
        geneData = []

        query = """
                MATCH (n)-[:INSIDE*]->(t:Transcript)-[:INSIDE]->(g:Gene)
                WHERE g.chrom = $chrom AND g.start <= $end AND g.end >= $start
                RETURN g, t, n, labels(n) AS type
                """
        results = session.run(query, {"chrom": chrom, "start":start, "end":end})
        
        for result in results:
            gene = record.gene_record(result["g"])
            transcript = record.transcript_record(result["t"])
            type = result["type"][0]
            other = record.annotation_record(result["n"], type)
            geneData.append([gene, transcript, type, other])

    return create_gene_objects(geneData)
   

def get_genes_in_range(chrom, start, end):
    genes = query_gene_range( chrom, start, end)

    print(f"GENE QUERY: #{chrom}:{start}-{end}")
    print(f"   Genes: {len(genes)}")

    return genes




'''
# Function to create a full-text node index
def create_fulltext_node_index(driver):
    with driver.session() as session:
        session.write_transaction(_create_ft_index)

def _create_ft_index(tx):
    query = (
        "CALL db.index.fulltext.createNodeIndex("
        "'productSearch', ['Product'], ['name', 'description'])"
    )
    tx.run(query)

# Connect to Neo4j
driver = GraphDatabase.driver(uri, auth=(username, password))

# Create the full-text node index
create_fulltext_node_index(driver)

# Close the driver connection when done
driver.close()

#===============================================


# Function to perform a full-text search
def fulltext_search(driver, search_term):
    with driver.session() as session:
        result = session.read_transaction(_search_ft_index, search_term)
        return [record for record in result]

def _search_ft_index(tx, search_term):
    query = (
        "CALL db.index.fulltext.queryNodes('productSearch', $term) "
        "YIELD node, score "
        "RETURN node.name, node.description, score"
    )
    return tx.run(query, term=search_term)

# Search term
search_term = "yourSearchTerm"  # Replace with your search term

# Perform the search
search_results = fulltext_search(driver, search_term)

# Print results
for result in search_results:
    print(result)


'''




