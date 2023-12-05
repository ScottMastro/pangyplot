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



