import time
import sys
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

def parse_line_S(line, ref, refSet, positions, layoutCoords):
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
 
#compresses link data into a binary number (0 absent, 1 present), stored as integer
def collapse_binary(path, pathDict, sampleIdDict):
    sampleIdx = sampleIdDict[path_id(path)]
    for i in range(len(path["path"]) - 1):
        key = (path["path"][i], path["path"][i + 1])
        if key not in pathDict:
            pathDict[key] = 0
        pathDict[key] |= (1 << sampleIdx)
    return pathDict

def update_sample_codes(path, sampleIdDict):
    sampleId = path_id(path)
    if sampleId not in sampleIdDict:
        if len(sampleIdDict) == 0:
            sampleIdDict[sampleId] = 0
        else:
            sampleIdDict[sampleId] = max([sampleIdDict[x] for x in sampleIdDict])+1

    return sampleIdDict

def get_ref_id(ref, sampleIdDict):
    matching_refs = [sample_name for sample_name in sampleIdDict if ref in sample_name]

    if len(matching_refs) == 0:
        print(f"\nERROR: Reference sample '{ref}' not found in any sample IDs.")
        sys.exit(1)
    elif len(matching_refs) > 1:
        print(f"\nERROR: Reference sample string '{ref}' matched multiple samples:")
        for name in matching_refs:
            print(f"  - {name}")
        print("Please provide a more specific reference name.")
        sys.exit(1)

    ref_sample_id = matching_refs[0]
    ref_sample_idx = sampleIdDict[ref_sample_id]
    print(f"\nFound reference sample: '{ref_sample_id}' (id={ref_sample_idx})")
    return ref_sample_idx

def parse_graph(gfa, ref, positions, layoutCoords):
    lenDict = dict()
    sampleIdDict = dict()
    pathDict = dict()

    refSet = set()

    # ==== PATHS ====
    pathCount = 0
    start_time = time.time()
    print("Gathering paths from GFA...")

    with get_reader(gfa) as gfaFile:
        for line in gfaFile:
            if line[0] in "PW":
                path = parse_line_P(line) if line[0] == "P" else parse_line_W(line)
                pathCount += 1
                if ref in path["sample"]:
                    refSet.update({p[:-1] for p in path["path"]}) # remove strand info
                sampleIdDict = update_sample_codes(path, sampleIdDict)
                pathDict = collapse_binary(path, pathDict, sampleIdDict)

                if pathCount % 1000 == 0:
                    elapsed = time.time() - start_time
                    rate = pathCount / elapsed
                    
                    sys.stdout.write( f"\rRead {pathCount:,} paths at {rate:,.1f}/sec" )
                    sys.stdout.flush()
    print()  # new line

    samples = [{"id": sample_name, "idx": sample_idx} for sample_name, sample_idx in sampleIdDict.items()]
    refIdx = get_ref_id(ref, sampleIdDict)
    insert_samples(samples)
    
    # ==== SEGMENTS ====
    print("Gathering segments from GFA and batch uploading...")
    segments = []
    segmentCount = 0
    start_time = time.time()

    with get_reader(gfa) as gfaFile:
        for line in gfaFile:
            if line[0] == "S":
                segment = parse_line_S(line, ref, refSet, positions, layoutCoords)
                lenDict[segment["id"]] = segment["length"]
                for c in ["x1", "y1", "x2", "y2"]:
                    segment[c] = layoutCoords[segmentCount][c]
                segment["is_ref"] = segment["id"] in refSet
                segments.append(segment)
                segmentCount += 1

                if len(segments) > 100000:
                    insert_segments(segments)
                    segments = []

                    elapsed = time.time() - start_time
                    rate = segmentCount / elapsed
                    sys.stdout.write(f"\rProcessed {segmentCount:,} segments at {rate:,.1f}/sec")
                    sys.stdout.flush()

    insert_segments(segments) ; segments = []
    print()  # new line

    # ==== LINKS ====
    def process_path_information(links):
        n = max([sampleIdDict[x] for x in sampleIdDict]) + 1
        for link in links:

            key = (f"{link['from_id']}{link['from_strand']}",
                   f"{link['to_id']}{link['to_strand']}")
            keyReverse = reverse_key(key)

            mask = 0
            if key in pathDict:
                mask |= pathDict[key]
            if keyReverse in pathDict:
                mask |= pathDict[keyReverse]
                
            # We store the haplotype bitmask as a hex string (e.g., '0x2fa')
            # to avoid integer overflow in Neo4j Bolt protocol (>64-bit ints not supported)
            link["haplotype"] = hex(mask)[2:]  # e.g., '2fa'
            link["frequency"] = bin(mask).count("1") / n
            link["reverse"] = hex(pathDict[keyReverse])[2:] if keyReverse in pathDict else "0"
            link["is_ref"] = ((mask >> refIdx) & 1) == 1

        return links

    print("Gathering links from GFA and batch uploading...")
    links = []
    linkCount = 0
    start_time = time.time()

    with get_reader(gfa) as gfaFile:
        for line in gfaFile:
            if line[0] == "L":
                link = parse_line_L(line)
                links.append(link)
                linkCount += 1

                if len(links) > 100000:
                    links = process_path_information(links)
                    insert_segment_links(links)
                    links = []

                    elapsed = time.time() - start_time
                    rate = linkCount / elapsed
                    sys.stdout.write(f"\rProcessed {linkCount} links at {rate:.1f}/sec")
                    sys.stdout.flush()


    links = process_path_information(links); links = []
    insert_segment_links(links)
    print()


