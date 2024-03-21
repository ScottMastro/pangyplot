import gzip
import parser.parse_utils as utils

def get_reader(positions_file):
    if positions_file.endswith(".gz"):
        return gzip.open(positions_file, 'rt')
    return open(positions_file)

def parse_line(line):

    cols = line.strip().split("\t")
    nodeId, startCol, endCol = cols

    startPath, startPos = startCol.split(":")
    endPath, endPos = endCol.split(":")
    
    start = utils.parse_reference_string(startPath)
    end = utils.parse_reference_string(endPath)

    if start["genome"] != end["genome"]:
        return None

    if start["chrom"] != end["chrom"]:
        return None

    result = {"genome": start["genome"], "chrom": start["chrom"],
                "start":int(startPos), "end":int(endPos) }
    return (nodeId, result)

def parse_positions(positions_file):
    skipFirstLine = False
    positions = dict()
    
    with get_reader(positions_file) as file:
        for line in file:
            if skipFirstLine:
                skipFirstLine=False
                continue

            data = parse_line(line)
            if data is not None:
                positions[data[0]] = data[1]
    return positions