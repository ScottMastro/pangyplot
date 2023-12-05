import gzip, re

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
    ids.append(path[pos:])
    return ids, strands


#TODO: change to length query directly
def get_lengths_by_id(node_ids):
    pass
    '''
    with get_session() as session:

        query = """
        UNWIND $ids AS id
        MATCH (n:Segment)
        WHERE n.id = id
        RETURN id, n.sequence AS seq
        """
        parameters = {'ids': node_ids}
        results = session.run(query, parameters)

        lengths = {result['id']: len(result['seq']) for result in results}
        return lengths
    '''

def assign_positions(qstart, rstart, path, cigar):
    nodeIds, _ = path_to_lists(path)
    lengths = get_lengths_by_id(nodeIds)
    print(lengths)
    cigarOps = re.findall('(\d+)([=XDI])', cigar)

    query_positions = {}
    cigarIndex = 0
    currentPosQ = 0
    flag = True
    for nodeId in nodeIds:
        currentPosR = rstart if flag else 0
        nodeLen = lengths[nodeId]
        start = None if flag else qstart + currentPosQ + 1
        flag = False

        while cigarIndex < len(cigarOps) and currentPosR < nodeLen:
            opLen, opType = cigarOps[cigarIndex]
            opLen = int(opLen)

            if opType in "=XD":  # Match or Mismatch
                advance = min(opLen, nodeLen - currentPosR)
                currentPosR += advance
                if opType != "D": # Deletion - Adjust only the reference sequence position
                    currentPosQ += advance
                if advance < opLen:
                    cigarOps[cigarIndex] = (opLen - advance, opType)
                    continue

            elif opType == "I": # Insertion - Adjust only the query sequence position
                currentPosQ +=opLen

            cigarIndex += 1

        end = qstart + currentPosQ
        query_positions[nodeId] = {'start': start, 'end': end}

    query_positions[nodeId]["end"] = None
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
    result["rlen"] = int(cols[6])
    result["rstart"] = int(cols[7])
    result["rend"] = int(cols[8])
    result["matches"] = int(cols[9])
    result["alen"] = int(cols[10])

    otherDict = {}
    for col in cols[12:]:
        key,type,value = col.split(":")
        otherDict[key] = value

    result["cigar"] = otherDict["cg"]
    coords = assign_positions(result["qstart"], result["rstart"], result["path"], result["cigar"])
    
    return coords

def parse_coords(gaf):
    coords = {}
    with get_reader(gaf) as file:
        for line in file:
            alnCoords = parse_line(line)
            for nodeId in alnCoords:
                if nodeId not in coords:
                    coords[nodeId] = alnCoords[nodeId]
                else: 
                    print("WOAH")
            print(coords)
            
            