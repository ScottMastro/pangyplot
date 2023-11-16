import gzip
import data.neo4j_query as q
import re

# https://github.com/lh3/gfatools/blob/master/doc/rGFA.md

def get_reader(gaf):
    if gaf.endswith(".gz"):
        return gzip.open(gaf, 'rt')
    return open(gaf)

def path_to_lists(path):
    ids, strands = [], []
    pos=0
    for i,char in enumerate(path):
        if char == ">" or char == "<":
            strand = "+" if char == ">" else "-"
            strands.append(strand)
            if i != 0: ids.append(path[pos:i])
            pos=i+1

    return ids, strands


def assign_positions(qstart, qend, path, cigar):

    nodeIds, _ = path_to_lists(path)
    lengths = q.get_lengths_by_id(nodeIds)
    cigarOps = re.findall('(\d+)([=XDI])', cigar)

    query_positions = {}
    cigarIndex = 0
    currentPosQ = 0
    
    for nodeId in nodeIds:
        currentPosR = 0
        nodeLen = lengths[nodeId]
        start = qstart + currentPosQ
        print("start", start, nodeId)

        print("op", cigarIndex < len(cigarOps), currentPosR < nodeLen)

        print("sum", sum ([int(x) for x, y in cigarOps if y in "=XI"]))
        print("length", qend - qstart)
        print("nodesum", sum([lengths[nodeId] for nodeId in nodeIds]))
        print("nodesum2", sum([int(x) for x, y in cigarOps if y in "=XD"]))

        while cigarIndex < len(cigarOps) and currentPosR < nodeLen:
            opLen, opType = cigarOps[cigarIndex]
            opLen = int(opLen)

            if opType in "=XI":  # Match or Mismatch
                advance = min(opLen, nodeLen - currentPosR)
                currentPosQ += advance 
                if opType != "I": # Insertion - Adjust only the query sequence position
                    currentPosR += advance
                if advance < opLen:
                    cigarOps[cigarIndex] = (opLen - advance, opType)
                    break
            elif opType == "D":  # Deletion - Adjust only the reference sequence position
                currentPosR +=opLen
            cigarIndex += 1

        end = qstart + currentPosQ
        query_positions[nodeId] = {'start': start, 'end': end}

    print(qend)
    print(qstart + currentPosQ)

    print(query_positions)
    return query_positions


def parse_line(line):

    if line.startswith("#"):
        return None
    
    result = dict()
    cols = line.strip().split("\t")
    
    result["qname"] = cols[0]
    result["qlen"] = int(cols[1])
    result["qstart"] = int(cols[2])
    result["qend"] = int(cols[3])
    result["strand"] = cols[4]
    result["path"] = cols[5]

    otherDict = {}
    for col in cols[12:]:
        key,type,value = col.split(":")
        otherDict[key] = value

    result["cigar"] = otherDict["cg"]
    nodes = assign_positions(result["qstart"], result["qend"], result["path"], result["cigar"])

    for c in result["info"].split(";"):
        if c.startswith("ID"):
            result["id"] = c.split("=")[1]
        if c.startswith("gene_name"):
            result["gene"] = c.split("=")[1]
        if c.startswith("exon_number"):
            result["exon"] = c.split("=")[1]
    
    return result

def parse_coords(gaf):
    alignments = []
    with get_reader(gaf) as file:
        for line in file:
            alignment = parse_line(line)
            print(alignment)
            alignments.append(alignment)
