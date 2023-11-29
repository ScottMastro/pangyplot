import sys, gzip

def get_reader(gfa):
    if gfa.endswith(".gz"):
        return gzip.open(gfa, 'rt')
    return open(gfa, 'r')

def add_to_dict(d, k, v):
    if k not in d:
        d[k] = []
    d[k].append(v)

def read_links(rgfa_file):
    in_links = dict()
    out_links = dict()

    with get_reader(rgfa_file) as file:
        for line in file:
            if line[0] == "L":
                parts = line.strip().split('\t')
                fromId, fromStrand, toId, toStrand = parts[1:5]
                fromId = int(fromId)
                toId = int(toId)
                fr = (toStrand, fromStrand, fromId)
                to = (fromStrand, toStrand, toId)
            
                add_to_dict(in_links, toId, fr)
                add_to_dict(out_links, fromId, to)

    return in_links, out_links

def compact_nodes(in_links, out_links):
    compactDict = dict()
    toRemove = set()

    for node in out_links:
        compactDict[node] = []
        if len(out_links[node]) == 1:
            strand, other_strand, other_node = out_links[node][0]
            if other_node in in_links and len(in_links[other_node]) == 1:
                toRemove.add(other_node)
                compactDict[node] = other_node
                print(strand, node, other_strand, other_node)

    return compactDict, toRemove

#def add_info_to_gfa(original_gfa_file, new_gfa_file, info_dict, length_dict):
#    with open(original_gfa_file, 'r') as infile, open(new_gfa_file, 'w') as outfile:
#        for line in infile:
#            if line.startswith('S'):
#                parts = line.strip().split('\t')
#                id = parts[1]
#                if id in info_dict:
#                    if len(parts[2]) != length_dict[id]:
#                        print("WARNING: sequence lengths don't match for ID="+str(id)+" (are your GFAs for the same graph?)")
#                    line = line.strip() + '\t' + info_dict[id] + '\n'
#            outfile.write(line)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python compact_rgfa.py input_rgfa")
        sys.exit(1)

    rgfa_file = sys.argv[1]

    eprint("Collecting L lines in rGFA...")
    in_links, out_links = read_links(rgfa_file)

    eprint("Compacting S lines in rGFA...")
    compactDict, toRemove = compact_nodes(in_links, out_links)

    print(compactDict)
    #basename_gfa = os.path.basename(rgfa_file)
    #new_gfa_file = "compact_" + basename_gfa

    #print("Reading GFA...")
    #info_dict, length_dict = read_rgfa(rgfa_file)
    #add_info_to_gfa(gfa_file, new_gfa_file, info_dict, length_dict)