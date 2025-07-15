import bisect

def parse_gfa_for_path_coords(gfa_path, target_path):
    """
    Extracts (node_id, start, end) coordinate tuples for a given path in a GFA file.
    """
    node_lengths = {}
    path_steps = []

    with open(gfa_path, 'r') as f:
        for line in f:
            if line.startswith('S'):
                parts = line.strip().split('\t')
                node_id = int(parts[1])
                sequence = parts[2]
                node_lengths[node_id] = len(sequence)

            elif line.startswith('P'):
                parts = line.strip().split('\t')
                path_name = parts[1]
                if path_name == target_path:
                    step_strs = parts[2].split(',')
                    for step in step_strs:
                        orient = step[-1]
                        node_id = int(step[:-1])
                        path_steps.append((node_id, orient))

    coords = []
    pos = 0
    for node_id, _ in path_steps:
        start = pos
        end = pos + node_lengths[node_id]
        coords.append((node_id, start, end))
        pos = end

    return coords

class PathPositionIndex:
    """
    Index mapping basepair positions to node intervals on a path.
    """
    def __init__(self, coords):
        self.coords = coords  # list of (node_id, start, end)
        self.starts = [start for _, start, _ in coords]

    def query_bp(self, bp_position):
        i = bisect.bisect_right(self.starts, bp_position) - 1

        if i < 0:
            return self.coords[0] 
        if i >= len(self.coords) or bp_position >= self.coords[i][2]:
            return self.coords[-1]

        return self.coords[i]  # (node_id, start, end)

    def query(self, start, end, debug=False):
        res1 = self.query_bp(start)
        res2 = self.query_bp(end)
        if debug:
            print(f"""[DEBUG] Position query results {start}-{end}. 
                  START: node {res1[0]} / ref coords {res1[1]}-{res1[2]}
                  END:   node {res2[0]} / ref coords {res2[1]}-{res2[2]}""")
        return (res1[0],res2[0])

def build_path_position_index(gfa_path, path_name):
    """
    Constructs a PathPositionIndex from a GFA file and a given path.
    """
    coords = parse_gfa_for_path_coords(gfa_path, path_name)
    return PathPositionIndex(coords)


def query_position_in_index(index, bp_position):
    """
    Queries a basepair position from a PathPositionIndex object.
    """
    return index.query(bp_position)
