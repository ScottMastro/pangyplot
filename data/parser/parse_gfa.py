import gzip
from math import nextafter
from statistics import mean
from tracemalloc import start
from data.model.segment import Segment
from data.model.link import Link
from data.model.path import Path

from collections import deque

def get_reader(gfa):
    if gfa.endswith(".gz"):
        return gzip.open(gfa, 'rt')
    return open(gfa)

def P_to_W(path):
    splitPath = path.split(",")
    newPath = ""
    for part in splitPath:
        if part[-1] == "+":
            newPath += ">" + part[:-1]
        elif part[-1] == "-":
            newPath += "<" + part[:-1]
    return newPath
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
                result["chrom"] = col.split(":")[-1]
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

    fromNodes = fromLinkData[id] if id in fromLinkData else []
    toNodes = toLinkData[id] if id in toLinkData else []

    estimatedFromPos = [] # based on nodes connecting to the target node
    estimatedFromChrom = []

    for fromId in fromNodes:
        if fromId in visited:
            continue
        chrom,pos,length = segmentData[fromId]
        if pos is None:
            chrom, pos = estimate_position(fromId, fromLinkData, toLinkData, segmentData, visited+[id])
        if pos is not None:
            estimatedFromPos.append(pos+length+1)
            estimatedFromChrom.append(chrom)

    estimatedToPos = [] # based on nodes the target node connects to
    estimatedToChrom = []

    for toId in toNodes:
        if toId in visited:
            continue
        chrom,pos,length = segmentData[toId]
        if pos is None:
            chrom, pos = estimate_position(toId, fromLinkData, toLinkData, segmentData, visited+[id])
        if pos is not None:
            estimatedToPos.append(pos-segmentData[id][2]-1)
            estimatedToChrom.append(chrom)

    #print(id, estimatedFromPos, estimatedToPos)
    chroms = estimatedFromChrom+estimatedToChrom

    if len(chroms) == 0:
        return None,None

    chrom = max(set(chroms), key = chroms.count)

    pos = mean([x for c,x in zip(chroms, estimatedFromPos+estimatedToPos) if c == chrom])
    pos = round(pos)
    segmentData[id] = (chrom, pos, segmentData[id][2])

    return chrom, pos

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
