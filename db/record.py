
def chain_record(record):
    chain = {k: record[k] for k in record.keys()}
    chain["type"] = "chain"
    # NOTE: r.id is the neo4j node id and r["id"] is the chain id
    chain["nodeid"] = record.id
    return chain

def bubble_record(record):
    bubble = {k: record[k] for k in record.keys()}
    bubble["type"] = "bubble"
    # NOTE: r.id is the neo4j node id and r["id"] is the bubble id
    bubble["nodeid"] = record.id
    return bubble

def segment_record(record):
    segment = {k: record[k] for k in record.keys()}
    segment["type"] = "segment"
    if segment["length"] == 0: 
        segment["type"] = "null" 
    # NOTE: r.id is the neo4j node id and r["id"] is the gfa id
    segment["nodeid"] = record.id
    return segment

def node_record(record, nodeType):
    if nodeType == "Segment":
        return segment_record(record) 
    if  nodeType == "Chain":
        return chain_record(record) 
    if nodeType == "Bubble":
        return bubble_record(record)
    return None

def node_records(records, key, typeKey):
    nodes = []
    for record in records:
        node = node_record(record[key], record[typeKey]) 
        nodes.append(node)
    return nodes

def segment_records(records, key):
    nodes = []
    for record in records:
        node = segment_record(record[key]) 
        nodes.append(node)
    return nodes

def link_record_simple(record):
    link = {"source": record.start_node.id,
            "target": record.end_node.id,
            "class": "edge"}
    return link

def link_records_simple(records, key):
    links = []
    for record in records:
        for r in record[key]:
            link = link_record_simple(r)
            links.append(link)
    return links

def link_record(record):
    link = {"source": record.start_node.id,
            "target": record.end_node.id,
            "from_strand": record["from_strand"],
            "to_strand": record["to_strand"],
            "frequency": record["frequency"],
            "haplotype": record["haplotype"],
            "class": "edge"}
    return link

def link_records(records, key):
    links = []
    for record in records:
        for r in record[key]:
            link = link_record(r)
            links.append(link)
    return links