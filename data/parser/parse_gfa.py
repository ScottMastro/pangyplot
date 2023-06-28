import gzip
from data.model.segment import Segment
from data.model.link import Link

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
                result["pos"] = col.split(":")[-1]
            elif col.startswith("SR:"):
                result["sr"] = col.split(":")[-1]

    return result

def populate_gfa(db, gfa, count_update):
    count = 0
    segmentId = 0

    with get_reader(gfa) as file:
        for line in file:
            row = parse_line(line)
            if row["type"] == "L":
                link = Link(row)
                db.session.add(link)

            elif row["type"] == "S":
                row["nodeid"] = row["id"]
                row["id"] = segmentId
                segmentId += 1

                segment = Segment(row)
                db.session.add(segment)

            count += 1
            count_update(count)
        
        db.session.commit()