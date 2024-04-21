import argparse
from collections import deque

def parse_gfa_file(gfa, ref):
    graph = dict()
    lenDict = dict()
    paths = []
    
    with open(gfa, 'r') as file:
        for line in file:

            parts = line.strip().split('\t')
            line_type = parts[0]
            
            if line_type == 'S':
                sid = parts[1]
                lenDict[sid] = len(parts[2])

                if sid not in graph:
                    graph[sid] = {"to": set(), "from": set()}

            elif line_type == 'L':
                from_segment = parts[1]
                to_segment = parts[3]
                
                from_strand = parts[2]
                to_strand = parts[4]

                if from_strand == "-" and to_strand == "-":
                    to_segment, from_segment = from_segment, to_segment
                    from_strand = "+"; to_strand = "+"
                
                if from_segment not in graph:
                    graph[from_segment] = {"to": set(), "from": set()}
                if to_segment not in graph:
                    graph[to_segment] = {"to": set(), "from": set()}

                graph[from_segment]["to"].add(to_segment)
                graph[to_segment]["from"].add(from_segment)

                if from_strand == "-" or to_strand == "-":
                    print(from_segment, to_segment)
                    graph[from_segment]["from"].add(to_segment)
                    graph[to_segment]["to"].add(from_segment)



            elif line_type == 'P' or line_type == 'W':
                if not parts[1].startswith(ref):
                    continue

                genome = ref
                start = 0
                chrom = "?"

                if line_type == 'P':
                    pathname = parts[1]

                    if "#" in pathname:
                        genome = pathname.split("#")[0]
                        pathname = pathname.split("#")[-1]

                    if ":" in pathname:
                        chrom = pathname.split(":")[0]
                        pathname = pathname.split(":")[-1]

                    if "-" in pathname:
                        start = int(pathname.split("-")[0])
                        end = int(pathname.split("-")[-1])

                    path = parts[2]
                    path = path.replace("+", "").replace("-", ",")

                if line_type == 'W':
                    genome = parts[1]
                    chrom = parts[3]
                    start = int(parts[4])
                    end = int(parts[5])
                    path = parts[6]
                    path = path.replace("<", ",").replace(">", ",")

                paths.append({"genome": genome,
                              "chrom": chrom,
                              "start": start,
                              "path": path.split(',')})
    return graph, lenDict, paths

def calculate_path_positions(lenDict, paths):
    positions = dict()

    for path in paths:
        pos = path["start"]

        for segment in path["path"]:
            if segment not in positions:
                positions[segment] = []

            positions[segment].append([path["genome"], path["chrom"], pos])
            pos += lenDict[segment]

    return positions

def print_result(sid, genome, chrom, start, dist1, end, dist2):
    prefix = genome+"#"+chrom+":"
    print(sid + "\t" + prefix + str(start) + "\t" + str(dist1) +
                "\t" + prefix + str(end)   + "\t" + str(dist2))

def bfs_find_position(graph, start_id, direction, ref_positions, lenDict):
    queue = deque([(start_id, 0)])
    visited = set()
    tabs = ""
    while queue:
        current, dist = queue.popleft()
        tabs = tabs + " "
        print(tabs, current)
        input()

        if current in visited:
            continue
        visited.add(current)

        if current in ref_positions:
            return current, dist

        if direction == "to" and current in graph and "to" in graph[current]:
            for neighbor in graph[current]["to"]:
                if neighbor in lenDict:
                    queue.append((neighbor, dist + lenDict[neighbor]))
        elif direction == "from" and current in graph and "from" in graph[current]:
            for neighbor in graph[current]["from"]:
                if neighbor in lenDict:
                    queue.append((neighbor, dist - lenDict[neighbor]))

    return None, None

def calculate_inferred_positions(graph, ref_positions, lenDict):
    ids = sorted(graph.keys(), key=int)

    for sid in ids:
        if sid in ref_positions:
            genome, chrom, start = ref_positions[sid][0]
            end = start + lenDict[sid]
            print_result(sid, genome, chrom, start, 0, end, 0)
        else:
            closest_to, dist_to = bfs_find_position(graph, sid, "to", ref_positions, lenDict)
            closest_from, dist_from = bfs_find_position(graph, sid, "from", ref_positions, lenDict)

            if closest_to is None and closest_from is None:
                continue

            elif closest_to is not None and closest_from is None:
                genome, chrom, pos = ref_positions[closest_to][0]
                print_result(sid, genome, chrom, pos, dist_to, pos, None)

            elif closest_to is None and closest_from is not None:
                genome, chrom, pos = ref_positions[closest_from][0]
                pos = pos + lenDict[closest_from]
                print_result(sid, genome, chrom, pos, None, pos, dist_from)

            else:
                genome, chrom, end = ref_positions[closest_to][0]
                _, _, start = ref_positions[closest_from][0]
                start = start + lenDict[closest_from]
                if start > end:
                    temp = start
                    start = end
                    end = temp

                print_result(sid, genome, chrom, start, dist_to, end, dist_from)

def main():
    parser = argparse.ArgumentParser(description='Parse a GFA file and store connections in a graph structure.')
    parser.add_argument('ref', type=str, help='The reference genome name (should be a path in the GFA)')
    parser.add_argument('gfa', type=str, help='Path to the GFA file')
    
    args = parser.parse_args()

    ref = args.ref
    if "#" in args.ref:
        ref = ref.split("#")[0]
    gfa = args.gfa

    graph, lenDict, paths = parse_gfa_file(gfa, ref)

    ref_positions = calculate_path_positions(lenDict, paths)

    positions = calculate_inferred_positions(graph, ref_positions, lenDict)




if __name__ == '__main__':
    main()
