
def chain_record(record):
    chain = {k: record[k] for k in record.keys()}
    chain["nodeid"] = chain.pop("uuid", None)
    chain["type"] = "chain"
    return chain

def bubble_record(record):
    bubble = {k: record[k] for k in record.keys()}
    bubble["nodeid"] = bubble.pop("uuid", None)
    bubble["type"] = "bubble"
    return bubble

def segment_record(record):
    segment = {k: record[k] for k in record.keys()}
    segment["nodeid"] = segment.pop("uuid", None)
    segment["type"] = "segment"
    if segment["length"] == 0: 
        segment["type"] = "null"
    return segment

def cluster_record(record):
    cluster = {k: record[k] for k in record.keys()}
    cluster["type"] = "cluster"
    return cluster

def node_record(record, nodeType):
    if nodeType == "Segment":
        return segment_record(record) 
    if  nodeType == "Chain":
        return chain_record(record) 
    if nodeType == "Bubble":
        return bubble_record(record)
    return None

def link_record_simple(record):
    link = {"source": record.start_node.id,
            "target": record.end_node.id,
            "class": "edge"}
    return link

def link_record(record):
    link = {"source": record.start_node["uuid"],
            "target": record.end_node["uuid"],
            "from_strand": record["from_strand"],
            "to_strand": record["to_strand"],
            "frequency": record["frequency"],
            "haplotype": record["haplotype"],
            "reverse": record["reverse"],
            "is_ref": record["is_ref"],
            "is_del": record["is_del"],
            "class": "edge"}
    if link["haplotype"] is None:
        link["haplotype"] = "0"
    return link


def gene_annotation_record(record):
    data = {k: record[k] for k in record.keys()}
    return data

def gene_record(record):
    gene = {k: record[k] for k in record.keys()}
    return gene
def transcript_record(record):
    transcript = {k: record[k] for k in record.keys()}
    return transcript
def exon_record(record):
    exon = {k: record[k] for k in record.keys()}
    return exon


def annotation_record(record, nodeType):
    if nodeType == "Gene":
        return gene_record(record)
    if nodeType == "Exon":
        return gene_annotation_record(record)
    if  nodeType == "Transcript":
        return transcript_record(record) 
    if nodeType == "CDS":
        return gene_annotation_record(record)
    if nodeType == "Codon":
        return gene_annotation_record(record)
    if nodeType == "UTR":
        return gene_annotation_record(record)
    return None
