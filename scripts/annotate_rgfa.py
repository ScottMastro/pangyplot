import sys, gzip, os

def get_reader(gfa):
    if gfa.endswith(".gz"):
        return gzip.open(gfa, 'rt')
    return open(gfa, 'r')

def read_rgfa(rgfa_file):
    info_dict = {}
    length_dict = {}
    with get_reader(rgfa_file) as file:
        for i,line in enumerate(file):
            if line[0] == "S":
                parts = line.strip().split('\t')
                id = parts[1]  # assuming id is always the second element
                info = '\t'.join(parts[3:])  # additional information
                info_dict[id] = info
                length_dict[id] = len(parts[2])
                if i % 100000 == 0:
                    print(".", end="", flush=True)
    return info_dict, length_dict

def add_info_to_gfa(original_gfa_file, new_gfa_file, info_dict, length_dict):
    with open(original_gfa_file, 'r') as infile, open(new_gfa_file, 'w') as outfile:
        for line in infile:
            if line.startswith('S'):
                parts = line.strip().split('\t')
                id = parts[1]
                if id in info_dict:
                    if len(parts[2]) != length_dict[id]:
                        print("WARNING: sequence lengths don't match for ID="+str(id)+" (are your GFAs for the same graph?)")
                    line = line.strip() + '\t' + info_dict[id] + '\n'
            outfile.write(line)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python annotate_rgfa.py rgfa.gfa gfa.gfa")
        sys.exit(1)

    print("Reading rGFA...")
    rgfa_file = sys.argv[1]
    gfa_file = sys.argv[2]

    basename_gfa = os.path.basename(gfa_file)
    new_gfa_file = "annotated_" + basename_gfa

    print("Reading GFA...")
    info_dict, length_dict = read_rgfa(rgfa_file)
    add_info_to_gfa(gfa_file, new_gfa_file, info_dict, length_dict)