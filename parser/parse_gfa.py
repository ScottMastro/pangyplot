import gzip,re
import parser.parse_utils as utils
from statistics import mean
from db.insert.insert_segment import insert_segments, insert_segment_links

def get_reader(gfa):
    if gfa.endswith(".gz"):
        return gzip.open(gfa, 'rt')
    return open(gfa)

def extract_chrom(s):
    match = re.search(r'chr[a-zA-Z0-9]+', s)
    if match:
        return match.group()
    return None

def parse_line(line):

    result = {"type" : "."}

    if line[0] == "L":
        result["type"] = "L"
        cols = line.strip().split("\t")
        result["from_id"]=cols[1]
        result["from_strand"]=cols[2]
        result["to_id"]=cols[3]
        result["to_strand"]=cols[4]
    
    if line[0] == "S":
        result["type"] = "S"
        result["chrom"] = None
        result["pos"] = None

        cols = line.strip().split("\t")
        
        result["id"] = cols[1]
        result["seq"] = cols[2]

        for col in cols[3:]:
            if col.startswith("SN:"):
                result["chrom"] = extract_chrom(col.split(":")[-1])
            elif col.startswith("SO:"):
                # add 1 to position
                result["pos"] = int(col.split(":")[-1]) +1
            elif col.startswith("SR:"):
                result["sr"] = col.split(":")[-1]
        result["ref"] = result["pos"] is not None

    if line[0] == "P":
        cols = line.strip().split("\t")
        result["type"] = "P"
        result["sample"] = cols[1]
        result["hap"] = None
        result["start"] = None
        result["end"] = None
        result["path"], result["strand"] = path_to_lists(P_to_W(cols[2]))

    if line[0] == "W":
        cols = line.strip().split("\t")
        result["type"] = "W"
        result["sample"] = cols[1]
        result["hap"] = cols[2]
        result["start"] = cols[4]
        result["end"] = cols[5]
        result["path"], result["strand"] = path_to_lists(cols[6])

    return result

def collect_position_data(gfa):

    toLinkData = dict()
    fromLinkData = dict()
    segmentData = dict()

    with get_reader(gfa) as file:
        for line in file:
            row = parse_line(line)
            if row["type"] == "L":
                from_id, to_id = row["from_id"], row["to_id"]
                if from_id not in toLinkData:
                    toLinkData[from_id] = []
                toLinkData[from_id].append(to_id)
                if to_id not in fromLinkData:
                    fromLinkData[to_id] = []
                fromLinkData[to_id].append(from_id)
            elif row["type"] == "S":
                segmentData[row["id"]] = (row["chrom"],row["pos"], len(row["seq"]))

    return fromLinkData, toLinkData, segmentData

def parse_line_S(line, ref, positions):

    result = {"type" : "S"}   
    cols = line.strip().split("\t")
    
    id = cols[1]
    result["id"] = id
    result["seq"] = cols[2]
    result["gc_count"] = cols[2].count('G') + cols[2].count('C') + cols[2].count('g') + cols[2].count('c')
    result["length"] = len(cols[2])

    for key in ["genome", "chrom", "pos", "sr", "start", "end"]:
        result[key]= None

    if id in positions:
        for key in ["genome", "chrom", "start", "end"]:
            result[key] = positions[id][key]

    genome = None
    for col in cols[3:]:
        if col.startswith("SN:"):
            tigId = col.split(":")[-1]
            result = utils.parse_reference_string(tigId, ref=None)
            genome = result["genome"]
            chrom = result["chrome"]

        elif col.startswith("SO:"):
            # add 1 to position
            position = int(col.split(":")[-1]) +1
            start = position
            end = position + result["length"] -1
        elif col.startswith("SR:"):
            result["sr"] = col.split(":")[-1]

    if genome is not None and genome == ref:
        result["genome"] = genome
        result["chrom"] = chrom
        result["start"] = start
        result["end"] = end

    return result
    
def parse_line_L(line):

    result = {"type" : "L"}   
    cols = line.strip().split("\t")

    result["from_id"]=cols[1]
    result["from_strand"]=cols[2]
    result["to_id"]=cols[3]
    result["to_strand"]=cols[4]
    return result

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

def P_to_W(path):
    splitPath = path.split(",")
    newPath = ""
    for part in splitPath:
        if part[-1] == "+":
            newPath += ">" + part[:-1]
        elif part[-1] == "-":
            newPath += "<" + part[:-1]
    return newPath

def parse_line_P(line):

    result = {"type" : "P"}   
    cols = line.strip().split("\t")

    result["type"] = "P"
    result["sample"] = cols[1]
    result["hap"] = None

    if "#" in result["sample"]:
        parts = cols[1].split("#")
        result["sample"] = parts[0]
        if len(parts[1]) == 1:
            result["hap"] = parts[1] 
        #todo: can maybe find [start-end]

    elif ":" in result["sample"] and "-" in result["sample"]:
        result["sample"] = cols[1].split(":")[0]
        result["start"] = int(cols[1].split(":")[1].split("-")[0])
        result["end"] = int(cols[1].split(":")[1].split("-")[1])
    else:
        result["start"] = None
        result["end"] = None
    result["path"], result["strand"] = path_to_lists(P_to_W(cols[2]))

    return result

def parse_line_W(line):

    result = {"type" : "W"}   
    cols = line.strip().split("\t")

    result["type"] = "W"
    result["sample"] = cols[1]
    result["hap"] = cols[2]
    result["start"] = cols[4]
    result["end"] = cols[5]
    result["path"], result["strand"] = path_to_lists(cols[6])

    return result

def get_path_positions(path, lenDict):
    pos = int(path["start"])
    positions = [pos]
    for node in path["path"]:
        positions.append(pos)
        pos += lenDict[node]

    #TODO: the coordinates seem to be a bit off with this technique.
    #print(path["start"], positions[0], positions[-1], pos, path["end"])
    path["position"] = positions
    return path

def collapse_path(collapseDict, sampleIdDict, path, ):
    suffix = "" if path["hap"] is None else "." + path["hap"]
    sampleId = path["sample"] + suffix

    if sampleId not in sampleIdDict:
        if len(sampleIdDict) == 0:
            sampleIdDict[sampleId] = 0
        else:
            sampleIdDict[sampleId] = max([sampleIdDict[x] for x in sampleIdDict])+1
    sampleIdx = sampleIdDict[sampleId]

    for i,fromId in enumerate(path["path"][:-1]):
        toId = path["path"][i+1]
        fromStrand = path["strand"][i]
        toStrand = path["strand"][i+1]
        fromKey = str(fromId) + fromStrand
        toKey = str(toId) + toStrand
        key = (fromKey, toKey)
        if key not in collapseDict:
            collapseDict[key] = []
        
        collapseDict[key].append(sampleIdx)
    return collapseDict, sampleIdDict
   
def collapse_binary(collapseDict, sampleIdDict):
    n = max([sampleIdDict[x] for x in sampleIdDict])+1
    for key in collapseDict:
        idxs = collapseDict[key]
        boolList = [False] * n
        for idx in idxs:
            boolList[idx] = True
        collapseDict[key] = boolList
    return collapseDict

def parse_graph(gfa, ref, positions, layoutCoords):
    count = 0
    segmentCount = 0
    segments, links = [],[]
    lenDict = dict()
    collapseDict = dict()
    sampleIdDict = dict()
    refSet = set()

    print("Finding paths...")
    with get_reader(gfa) as gfaFile:
        count = 0
        for line in gfaFile:
            if line[0] in "PW":
                if line[0] == "P":
                    path = parse_line_P(line)
                else:
                    path = parse_line_W(line)
                #collapseDict, sampleIdDict = collapse_path(collapseDict, sampleIdDict, path)
                if ref in path["sample"]:
                    refSet.update(path["path"])
            count += 1
            if count % 10000 == 0:
                print(".", end='', flush=True)

    print("")
    print("Finding segments & links...")
    with get_reader(gfa) as gfaFile:
        count = 0
        for line in gfaFile:
            count+=1
            if line[0] == "S":
                segment = parse_line_S(line, ref, positions)
                lenDict[segment["id"]] = segment["length"]
                for c in ["x1", "y1", "x2", "y2"]:
                    segment[c] = layoutCoords[segmentCount][c]
                segment["is_ref"] = segment["id"] in refSet
                segments.append(segment)

                segmentCount += 1
            elif line[0] == "L":
                link = parse_line_L(line)
                links.append(link)

            if count % 100000 == 0:
                print(".", end='', flush=True)
            if len(segments) > 100000:
                insert_segments(segments)
                segments=[]

        if len(collapseDict) == 0:
            for link in links:
                link["haplotype"] = []
                link["frequency"] = 0
                link["is_ref"] = link["from_id"] in refSet and link["to_id"] in refSet

        else:

            collapseDict = collapse_binary(collapseDict, sampleIdDict)

            for link in links:
                key = (str(link["from_id"]) + link["from_strand"],
                        str(link["to_id"]) + link["to_strand"])
                #todo: line below does not account for strand
                link["is_ref"] = link["from_id"] in refSet and link["to_id"] in refSet
                if key in collapseDict:
                    hap = collapseDict[key]
                    link["haplotype"] = hap
                    link["frequency"] = sum(hap)/len(hap)
                else:
                    n = max([sampleIdDict[x] for x in sampleIdDict])+1
                    link["haplotype"] = [False] * n
                    link["frequency"] = 0

        insert_segments(segments)
        insert_segment_links(links)