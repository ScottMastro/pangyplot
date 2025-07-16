import sys
import gzip,re
import parser.parse_utils as utils
from collections import defaultdict

def get_reader(gfa_file):
    if gfa_file.endswith(".gz"):
        return gzip.open(gfa_file, 'rt')
    return open(gfa_file)

def extract_chrom(s):
    match = re.search(r'chr[a-zA-Z0-9]+', s)
    if match:
        return match.group()
    return None

def parse_line_S(line):
    segment = dict()
    cols = line.strip().split("\t")
    
    id = int(cols[1])
    segment["id"] = id
    seq = cols[2].upper()
    segment["seq"] = seq
    segment["gc_count"] = seq.count('G') + seq.count('C')
    segment["n_count"] = seq.count('N')
    segment["length"] = len(seq)
    return segment
    
def parse_line_L(line):
    link = dict()   
    cols = line.strip().split("\t")

    link["from_id"]=int(cols[1])
    link["from_strand"]=cols[2]
    link["to_id"]=int(cols[3])
    link["to_strand"]=cols[4]
    return link

def parse_line_P(line):
    path = dict()
    cols = line.strip().split("\t")

    path["full_id"] = cols[1]
    sampleInfo = utils.parse_id_string(cols[1])

    path["sample"] = sampleInfo["genome"]
    path["contig"] = sampleInfo["chrom"]
    path["hap"] = sampleInfo["hap"]
    path["start"] = sampleInfo["start"]
    path["path"] = cols[2].split(",")

    return path

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
    path = dict()
    cols = line.strip().split("\t")

    path["sample"] = cols[1]
    path["full_id"] = cols[1]
    path["hap"] = cols[2]
    path["start"] = cols[4]
    path["end"] = cols[5]
    path["path"] = path_from_W(cols[6])

    return path

def reverse_key(key):
    def flip(stranded_id):
        seg_id = stranded_id[:-1]
        strand = stranded_id[-1]
        flipped_strand = '-' if strand == '+' else '+'
        return seg_id + flipped_strand

    from_key, to_key = key
    return (flip(to_key), flip(from_key))

def verify_reference(ref_path, matching_refs):

    if len(matching_refs) == 0:
        print(f"   ❌ ERROR: Reference sample '{ref_path}' not found in any sample IDs.")
        sys.exit(1)
    elif len(matching_refs) > 1:
        print(f"   ❌ ERROR: Reference sample string '{ref_path}' matched multiple samples:")
        for name in matching_refs:
            print(f"     - {name}")
        print("   Please provide a more specific reference name.")
        sys.exit(1)

    print(f"   🎯 Found reference path {matching_refs[0]}.")


def parse_graph(gfa_file, ref_path, layout_coords):
    print("➡️ Parsing GFA.")

    ref_ids = set()
    
    # ==== PATHS ====
    sample_idx = dict()
    reference_idx = -1
    path_dict = defaultdict(int)
    matching_refs = []
    
    print("   🧵 Gathering paths from GFA...", end="")

    def collapse_binary(path):
        suffix = "" if path["hap"] is None else "." + path["hap"]
        pid = path["sample"] + suffix

        if pid not in sample_idx:
            if len(sample_idx) == 0:
                sample_idx[pid] = 0
            else:
                sample_idx[pid] = max([sample_idx[x] for x in sample_idx])+1
        idx = sample_idx[pid]

        #compresses path links into a binary number stored as integer
        path_list = path["path"]
        for i in range(len(path_list) - 1):
            key = (path_list[i], path_list[i + 1])
            path_dict[key] |= (1 << idx)

        return idx

    reference_path = None

    with get_reader(gfa_file) as gfa:
        for line in gfa:
            if line[0] in "PW":
                path = parse_line_P(line) if line[0] == "P" else parse_line_W(line)
                idx = collapse_binary(path)

                if ref_path in path["full_id"]:
                    matching_refs.append(path["full_id"])
                    ref_ids.update({int(p[:-1]) for p in path["path"]})
                    reference_path = path
                    reference_idx = idx

    print(" Done.")
    verify_reference(ref_path, matching_refs)

    # ==== SEGMENTS ====
    segments = dict()
    print("   🍡 Gathering segments from GFA and batch uploading...", end="")

    with get_reader(gfa_file) as gfa:
        counter = 0
        for line in gfa:
            if line[0] == "S":
                segment = parse_line_S(line)
                for c in ["x1", "y1", "x2", "y2"]:
                    segment[c] = layout_coords[counter][c]
                segment["ref"] = segment["id"] in ref_ids
                segments[segment["id"]] = segment
                counter += 1

    print(" Done.")

    # ==== LINKS ====
    links = defaultdict(list)
    print("   🧷 Gathering links from GFA and batch uploading...", end="")

    def process_path_information(link):
        n = len(sample_idx)

        key = (f"{link['from_id']}{link['from_strand']}",
               f"{link['to_id']}{link['to_strand']}")
        keyReverse = reverse_key(key)

        mask = 0
        if key in path_dict:
            mask |= path_dict[key]
        if keyReverse in path_dict:
            mask |= path_dict[keyReverse]
            
        # We store the haplotype bitmask as a hex string (e.g., '0x2fa')
        # to avoid integer overflow in Neo4j Bolt protocol (>64-bit ints not supported)
        link["haplotype"] = hex(mask)[2:]  # e.g., '2fa'
        link["frequency"] = bin(mask).count("1") / n
        link["reverse"] = hex(path_dict[keyReverse])[2:] if keyReverse in path_dict else "0"
        link["ref"] = ((mask >> reference_idx) & 1) == 1

    with get_reader(gfa_file) as gfa:
        for line in gfa:
            if line[0] == "L":
                link = parse_line_L(line)
                fid = int(link["from_id"])
                tid = int(link["to_id"])
                links[(fid,tid)] = link
                process_path_information(link)

    print(" Done.")

    return segments, links, reference_path, sample_idx