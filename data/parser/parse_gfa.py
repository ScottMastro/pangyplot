import gzip

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
