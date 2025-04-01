import gzip,re
import parser.parse_utils as utils
from statistics import mean
from db.insert.insert_segment import insert_segments, insert_segment_links
from db.insert.insert_sample import insert_samples

def get_reader(gfa):
    if gfa.endswith(".gz"):
        return gzip.open(gfa, 'rt')
    return open(gfa)

def extract_chrom(s):
    match = re.search(r'chr[a-zA-Z0-9]+', s)
    if match:
        return match.group()
    return None

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

def parse_line_P(line):

    result = {"type" : "P"}   
    cols = line.strip().split("\t")
    sampleInfo = utils.parse_id_string(cols[1])
    result["sample"] = sampleInfo["genome"]
    result["contig"] = sampleInfo["chrom"]
    result["hap"] = sampleInfo["hap"]
    result["start"] = sampleInfo["start"]

    result["path"] = cols[2].split(",")

    return result

def path_from_W(path_str):
    path = []
    pos = 0
    for i, char in enumerate(path_str):
        if char in "><":
            if i != 0:
                seg_id = path_str[pos:i]
                strand = "+" if path_str[i - 1] == ">" else "-"
                path.append(seg_id + strand)
            pos = i + 1
    # Append last
    seg_id = path_str[pos:]
    strand = "+" if path_str[pos - 1] == ">" else "-"
    path.append(seg_id + strand)
    return path

def parse_line_W(line):

    result = {"type" : "W"}   
    cols = line.strip().split("\t")

    result["sample"] = cols[1]
    result["hap"] = cols[2]
    result["start"] = cols[4]
    result["end"] = cols[5]
    result["path"] = path_from_W(cols[6])

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

def path_id(path):
    suffix = "" if path["hap"] is None else "." + path["hap"]
    return path["sample"] + suffix

def reverse_key(key):
    def flip(stranded_id):
        seg_id = stranded_id[:-1]
        strand = stranded_id[-1]
        flipped_strand = '-' if strand == '+' else '+'
        return seg_id + flipped_strand

    from_key, to_key = key
    return (flip(to_key), flip(from_key))

def collapse_path(path, collapseDict, sampleIdDict):
    sampleIdx = sampleIdDict[path_id(path)]

    for i in range(len(path["path"]) - 1):
        fromKey = path["path"][i]
        toKey = path["path"][i + 1]
        key = (fromKey, toKey)

        if key not in collapseDict:
            collapseDict[key] = []
        collapseDict[key].append(sampleIdx)

    return collapseDict
   
def collapse_binary(collapseDict, sampleIdDict):
    n = max([sampleIdDict[x] for x in sampleIdDict])+1
    for key in collapseDict:
        idxs = collapseDict[key]
        boolList = [False] * n
        for idx in idxs:
            boolList[idx] = True
        collapseDict[key] = boolList
    return collapseDict

def update_sample_codes(path, sampleIdDict):

    sampleId = path_id(path)
    if sampleId not in sampleIdDict:
        if len(sampleIdDict) == 0:
            sampleIdDict[sampleId] = 0
        else:
            sampleIdDict[sampleId] = max([sampleIdDict[x] for x in sampleIdDict])+1

    return sampleIdDict

def parse_graph(gfa, ref, positions, layoutCoords):
    lenDict = dict()
    sampleIdDict = dict()
    collapseDict = dict()
    refSet = set()

    pathCount = 0

    print("Finding paths...")
    with get_reader(gfa) as gfaFile:
        for line in gfaFile:
            if line[0] in "PW":
                if line[0] == "P":
                    path = parse_line_P(line)
                else:
                    path = parse_line_W(line)

                pathCount += 1
                if ref in path["sample"]:
                    refSet.update(path["path"])

                sampleIdDict = update_sample_codes(path, sampleIdDict)
                collapseDict = collapse_path(path, collapseDict, sampleIdDict)

            if pathCount > 0 and pathCount % 10000 == 0:
                #print(path["sample"], path["hap"], path["start"])
                print(".", end='', flush=True)

    samples = [{"id": sample_name, "idx": sample_idx} for sample_name, sample_idx in sampleIdDict.items()]
    insert_samples(samples)
    
    collapseDict = collapse_binary(collapseDict, sampleIdDict)

    print("\nFinding segments...")
    segments = []
    segmentCount = 0
    with get_reader(gfa) as gfaFile:
        for line in gfaFile:
            if line[0] == "S":
                segment = parse_line_S(line, ref, positions)
                lenDict[segment["id"]] = segment["length"]
                for c in ["x1", "y1", "x2", "y2"]:
                    segment[c] = layoutCoords[segmentCount][c]
                segment["is_ref"] = segment["id"] in refSet
                segments.append(segment)

                segmentCount += 1

            if segmentCount % 100000 == 0:
                print(".", end='', flush=True)
            if len(segments) > 100000:
                insert_segments(segments)
                segments = []

    # Insert remaining segments after loop
    insert_segments(segments)

    def process_links(links):
        n = max([sampleIdDict[x] for x in sampleIdDict]) + 1

        for link in links:
            link["haplotype"] = [False] * n
            link["reverse"] = [False] * n
            link["frequency"] = 0
            
            #todo: line below does not account for strand 
            #later note: I think it is probably correct behaviour
            link["is_ref"] = link["from_id"] in refSet and link["to_id"] in refSet

            if len(collapseDict) == 0:
                continue

            key = (f"{link['from_id']}{link['from_strand']}",
                f"{link['to_id']}{link['to_strand']}")
            keyReverse = reverse_key(key)

            #todo: doesn't account for a path going through the same link multiple times
            if key in collapseDict:
                for i, val in enumerate(collapseDict[key]):
                    if val:
                        link["haplotype"][i] = True

            if keyReverse in collapseDict:
                for i, val in enumerate(collapseDict[keyReverse]):
                    if val:
                        link["haplotype"][i] = True
                        link["reverse"][i] = True   

            link["frequency"] = sum(link["haplotype"]) / n

        return links

    print("\nFinding links...")
    links = []
    linkCount = 0
    with get_reader(gfa) as gfaFile:
        for line in gfaFile:
            if line[0] == "L":
                link = parse_line_L(line)
                links.append(link)

                linkCount += 1

            if linkCount % 100000 == 0:
                print(".", end='', flush=True)
                links = process_links(links)
                insert_segment_links(links)
                links = []

    # Insert remaining links after loop
    links = process_links(links)
    insert_segment_links(links)
