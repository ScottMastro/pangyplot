import gzip

def get_reader(layout):
    if layout.endswith(".gz"):
        return gzip.open(layout, 'rt')
    return open(layout)

def parse_lines(line1, line2, line1Index):

    #skip first line
    if line1Index == 0:
        return None
    
    #skip lines that aren't paired
    if line1Index % 2 == 0:
        return None

    cols1 = line1.strip().split("\t")
    cols2 = line2.strip().split("\t")
    id = int(int(cols1[0])/2)

    result = dict()
    result["id"] = str(id)
    result["x1"] = cols1[1]
    result["y1"] = cols1[2]
    result["x2"] = cols2[1]
    result["y2"] = cols2[2]

    return result
