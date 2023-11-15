import re
import gzip
from statistics import mean
from data.model.segment import Segment
from data.model.link import Link
from data.model.path import Path
import data.neo4j_db as neo4jdb

import time

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

def estimate_position(id, fromLinkData, toLinkData, segmentData, visited=[]):

    return("chr7", 144123343)

    #print(id, len(visited))
    fromNodes = fromLinkData[id] if id in fromLinkData else []
    toNodes = toLinkData[id] if id in toLinkData else []

    estimatedFromPos = [] # based on nodes connecting to the target node
    estimatedFromChrom = []

    #print(visited )
    #print("from:", set(fromNodes).difference(set(visited)))
    for fromId in fromNodes:
        if (id,fromId) in visited:
            continue
        chrom,pos,length = segmentData[fromId]
        if pos is None:
            chrom, pos = estimate_position(fromId, fromLinkData, toLinkData, segmentData, visited+[(id,fromId)])
        if pos is not None:
            estimatedFromPos.append(pos+length+1)
            estimatedFromChrom.append(chrom)
            #print(chrom,pos)

    estimatedToPos = [] # based on nodes the target node connects to
    estimatedToChrom = []

    #print("to:", set(toNodes).difference(set(visited)))
    for toId in toNodes:
        if (toId,id) in visited:
            continue
        chrom,pos,length = segmentData[toId]
        if pos is None:
            chrom, pos = estimate_position(toId, fromLinkData, toLinkData, segmentData, visited+[(toId,id)])
        if pos is not None:
            estimatedToPos.append(pos-segmentData[id][2]-1)
            estimatedToChrom.append(chrom)

    #print(id, estimatedFromPos, estimatedToPos)
    chroms = estimatedFromChrom+estimatedToChrom
    #print(id, len(visited))

    if len(chroms) == 0:
        #todo:fix
        return None,None

    chrom = max(set(chroms), key = chroms.count)

    pos = mean([x for c,x in zip(chroms, estimatedFromPos+estimatedToPos) if c == chrom])
    pos = round(pos)
    segmentData[id] = (chrom, pos, segmentData[id][2])

    return chrom, pos


def parse_line_S(line):

    result = {"type" : "S"}   
    cols = line.strip().split("\t")
    
    result["id"] = cols[1]
    result["seq"] = cols[2]
    result["length"] = len(cols[2])

    return result
    """
    result["chrom"] = None
    result["pos"] = None
    for col in cols[3:]:
        if col.startswith("SN:"):
            result["chrom"] = extract_chrom(col.split(":")[-1])
        elif col.startswith("SO:"):
            # add 1 to position
            result["pos"] = int(col.split(":")[-1]) +1
        elif col.startswith("SR:"):
            result["sr"] = col.split(":")[-1]
    result["ref"] = result["pos"] is not None
    """
    
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
    result["start"] = None
    result["end"] = None
    result["path"], result["strand"] = path_to_lists(P_to_W(cols[2]))

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

def collapse_paths(collapseDict, sampleIdDict, path):

    sampleId = path["sample"] + "." + path["hap"]
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
        #position = path["position"][i]
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

def parse_graph(gfa, layoutCoords):
    count = 0
    segmentCount = 0
    segments, links = [],[]
    lenDict = dict()
    collapseDict = dict() ; collapsed = False
    sampleIdDict = dict()

    with get_reader(gfa) as gfaFile:
        
        for line in gfaFile:
            count+=1
            if line[0] == "S":
                segment = parse_line_S(line)
                lenDict[segment["id"]] = segment["length"]
                for c in ["x1", "y1", "x2", "y2"]:
                    segment[c] = layoutCoords[segmentCount][c]
                segments.append(segment)
                segmentCount += 1
            elif line[0] == "W":
                walk = parse_line_W(line)
                collapseDict, sampleIdDict = collapse_paths(collapseDict, sampleIdDict, walk)
                print("w", end='', flush=True)
                #walk = get_path_positions(walk, lenDict)
            elif line[0] == "P":
                path = parse_line_P(line)
            elif line[0] == "L":
                if not collapsed:
                    collapseDict = collapse_binary(collapseDict, sampleIdDict)
                    collapsed = True

                link = parse_line_L(line)
                key = (str(link["from_id"]) + link["from_strand"],
                       str(link["to_id"]) + link["to_strand"])
                if key in collapseDict:
                    hap = collapseDict[key]
                    link["haplotype"] = hap
                    link["frequency"] = sum(hap)/len(hap)
                else:
                    n = max([sampleIdDict[x] for x in sampleIdDict])+1
                    link["haplotype"] = [False] * n
                    link["frequency"] = 0
                links.append(link)

            if count % 100000 == 0:
                print(".")
            if len(segments) > 100000:
                neo4jdb.add_segments(segments)
                segments=[]
            if len(links) > 100000:
                neo4jdb.add_relationships(links)
                links=[]

        neo4jdb.add_segments(segments)
        neo4jdb.add_relationships(links)


def populate_gfa(db, gfa, count_update):
    count = 0
    segmentId = 0

    fromLinkData, toLinkData, segmentData = collect_position_data(gfa)

    with get_reader(gfa) as file:
        
        for line in file:
            row = parse_line(line)
            if row["type"] == "L":
                link = Link(row)
                db.session.add(link)

            elif row["type"] == "S":
                row["nodeid"] = row["id"]
                row["id"] = segmentId

                if row["pos"] is None:
                    chr, pos = estimate_position(row["nodeid"], fromLinkData, toLinkData, segmentData)
                    row["chrom"] = chr
                    row["pos"] = pos
                segmentId += 1
                
                segment = Segment(row)
                db.session.add(segment)

            count += 1
            count_update(count)
        
        db.session.commit()
    return segmentData

def populate_paths(db, segmentData, gfa, count_update):
    count = 0
    
    with get_reader(gfa) as file:
        for line in file:
            if len(line) > 0 and (line[0] == "P" or line[0] == "W"):
                row = parse_line(line)

                for i,(from_id,strand) in enumerate(zip(row["path"],row["strand"])):
                    
                    chrom,start,length = segmentData[from_id]

                    to_id = row["path"][i+1] if i+1 < len(row["path"]) else None
                    path = Path({"i": i,
                                "chrom": chrom,
                                "start": start,
                                "end": start+length,
                                "sample": row["sample"],
                                 "hap" : row["hap"],
                                 "from_id": from_id,
                                 "to_id": to_id,
                                 "strand": strand,
                                 })
                    db.session.add(path)

                count += 1
                count_update(count)
                
        db.session.commit()
