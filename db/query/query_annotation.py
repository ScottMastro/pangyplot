from operator import ge
from db.neo4j_db import get_session, GENE_TEXT_INDEX
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

#todo: do we care about transcript?
def query_gene_range_transcript(genome, chrom, start, end):
    with get_session() as (_, session):
        geneData = []

        query = """
                MATCH (n)-[:INSIDE*]->(t:Transcript)-[:INSIDE]->(g:Gene)
                WHERE g.genome = $genome AND g.chrom = $chrom AND g.start <= $end AND g.end >= $start
                RETURN g, t, n, labels(n) AS type
                """
        results = session.run(query, {"genome": genome, "chrom": chrom, "start":start, "end":end})
        
        for result in results:
            gene = record.gene_record(result["g"])
            transcript = record.transcript_record(result["t"])
            type = result["type"][0]
            other = record.annotation_record(result["n"], type)
            geneData.append([gene, transcript, type, other])

    return create_gene_objects(geneData)

def query_gene_range(genome, chrom, start, end):
    with get_session() as (_, session):
        geneData = []

        query = """
                MATCH (g:Gene)
                WHERE g.genome = $genome AND g.chrom = $chrom AND g.start <= $end AND g.end >= $start
                RETURN g
                """
        results = session.run(query, {"genome": genome, "chrom": chrom, "start":start, "end":end})
        
        for result in results:
            gene = record.gene_record(result["g"])
            geneData.append(gene)

    return geneData

def get_genes_in_range(genome, chrom, start, end):
    genes = query_gene_range(genome, chrom, start, end)

    print(f"GENE QUERY: {genome}#{chrom}:{start}-{end}")
    print(f"   Genes: {len(genes)}")

    return genes

def text_search_gene_query(session, searchTerm, before, after, maxResults=20):
    genes = []

    queryTerm = ("*" if before else "") + searchTerm +  ("*" if after else "")
    query = f"""
        CALL db.index.fulltext.queryNodes("{GENE_TEXT_INDEX}", "{queryTerm}")
        YIELD node, score
        RETURN node, score LIMIT {maxResults}
        """

    results = session.run(query)

    for result in results:
        gene = record.gene_record(result["node"])
        genes.append(gene)
    return genes

def text_search_gene(searchTerm, maxResults=20):
    with get_session() as (_, session):

        genes1 = text_search_gene_query(session, searchTerm, False, True, maxResults)
        
        if len(genes1) >= maxResults:
            return genes1

        genes2 = text_search_gene_query(session, searchTerm, True, True, maxResults)

    genes, geneSet = [], set()
    for gene in genes1+genes2:
        if gene["id"] not in geneSet:
            geneSet.add(gene["id"]) 
            genes.append(gene)

    return genes

