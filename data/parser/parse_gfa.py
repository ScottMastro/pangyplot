import gzip
from tracemalloc import start
from data.model.segment import Segment
from data.model.link import Link
from collections import deque

def get_reader(gfa):
    if gfa.endswith(".gz"):
        return gzip.open(gfa, 'rt')
    return open(gfa)

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

    return result

def collect_position_data(gfa):

    toLinkData = dict()
    fromLinkData = dict()
    segmentData = dict()

    with get_reader(gfa) as file:
        for line in file:
            row = parse_line(line)
            if row["type"] == "L":
                if row["to_id"] not in toLinkData:
                    toLinkData[row["to_id"]] = []
                if row["from_id"] not in fromLinkData:
                    fromLinkData[row["from_id"]] = []
                toLinkData[row["to_id"]].append(row["from_id"])
                fromLinkData[row["from_id"]].append(row["to_id"])
            elif row["type"] == "S":
                segmentData[row["id"]] = (row["chrom"],row["pos"], len(row["seq"]))

    return toLinkData, fromLinkData, segmentData

def estimate_position(startId, toLinkData, segmentData):

    visited = set()
    visited.add(startId)
    toVisit = deque()

    for id in toLinkData[startId]:
        toVisit.append([id, segmentData[id][2]])

    while len(toVisit) > 0:
        id,size = toVisit.popleft()
        chr,pos,length = segmentData[id]
        if pos is None:
            chr, pos = estimate_position(id, toLinkData, segmentData)
            segmentData[id] = (chr, pos, segmentData[id][2])
        else:
            segmentData[id] = (chr, pos, segmentData[id][2])
            return (chr, pos+size)

        visited.add(id)
        for nextId in toLinkData[id]:
            if id not in visited:
                toVisit.append([nextId, size+segmentData[nextId][2]])

    return (None, None)

def populate_gfa(db, gfa, count_update):
    count = 0
    segmentId = 0

    toLinkData, fromLinkData, segmentData = collect_position_data(gfa)

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
                    chr, pos = estimate_position(row["nodeid"], toLinkData, segmentData)
                    row["chrom"] = chr
                    row["pos"] = pos
                segmentId += 1
                
                segment = Segment(row)
                db.session.add(segment)

            count += 1
            count_update(count)
        
        db.session.commit()