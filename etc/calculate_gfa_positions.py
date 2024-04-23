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
                    graph[sid] = set()

            elif line_type == 'L':
                from_segment = parts[1]
                to_segment = parts[3]
            
                if from_segment not in graph:
                    graph[from_segment] = set()
                if to_segment not in graph:
                    graph[to_segment] = set()

                graph[from_segment].add(to_segment)
                graph[to_segment].add(from_segment)
                
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

def print_result2(sid, genome, chrom, start, dist1, end, dist2):
    prefix = genome+"#"+chrom+":"
    print(sid + "\t" + prefix + str(start) + "\t" + str(dist1) +
                "\t" + prefix + str(end)   + "\t" + str(dist2))
def print_result(sid, genome, chrom, start, end):
    prefix = genome+"#"+chrom+":"
    print(sid + "\t" + prefix + str(start) + "\t" + prefix + str(end) )

def bfs_find_position(graph, start_id, ref_positions, lenDict):
    queue = deque([(start_id, 0, "")])
    visited = set()
    distance = {start_id: 0}
    positions = []

    while queue:
        current, dist, tabs = queue.popleft()
        tabs = tabs + " "
        #print(tabs, current)

        if current in visited:
            continue
        visited.add(current)

        if current in ref_positions:
            positions.append([current, dist])
            continue

        for neighbor in graph[current]:
            new_dist = dist + lenDict[neighbor]
            if neighbor not in distance or new_dist < distance[neighbor]:
                distance[neighbor] = new_dist
                if neighbor not in visited:
                    queue.append((neighbor, new_dist, tabs))

    return positions

def bfs_find_subgraph(graph, start_id, ref_positions, lenDict):
    queue = deque([start_id])
    visited = set()
    refset = set()

    while queue:
        current = queue.popleft()

        if current in ref_positions:
            refset.add(current)
            continue

        if current in visited:
            continue

        visited.add(current)

        for neighbor in graph[current]:
            if neighbor not in visited:
                queue.append(neighbor)

    return refset, visited


def calculate_inferred_positions(graph, ref_positions, lenDict):
    ids = sorted(graph.keys())

    done = set()
    for sid in ids:
        if sid in ref_positions or sid in done:
            continue

        endpoints, subset = bfs_find_subgraph(graph, sid, ref_positions, lenDict)
        for x in subset:
            done.add(x)

        if len(subset) < 2:
            continue

        subgraph = {"ends": endpoints, "graph": subset}
        print(subgraph)
        input()










    for sid in ids:
        if sid in ref_positions:
            genome, chrom, start = ref_positions[sid][0]
            end = start + lenDict[sid]
            print_result(sid, genome, chrom, start, end)
    return

    for sid in ids:
        if sid in ref_positions:
            genome, chrom, start = ref_positions[sid][0]
            end = start + lenDict[sid]
            print_result2(sid, genome, chrom, start, 0, end, 0)
        else:
            positions = bfs_find_position(graph, sid, ref_positions, lenDict)

            if len(positions) == 0:
                continue

            max = None; maxdist = 0
            min = None; mindist = 0
            shortest = None; shortestdist = 0


            listy = []
            for sid,dist in positions:
                genome, chrom, refpos = ref_positions[sid][0]

                listy.append([genome, chrom, refpos, sid, dist, refpos-dist, refpos+dist])
                if max is None or refpos > max:
                    max = refpos
                    maxdist = dist
                if min is None or refpos < min:
                    min = refpos
                    mindist = dist
                if shortest is None or refpos < min:
                    min = refpos
                    mindist = dist

            
            listy.sort(key=lambda x: x[2])
            
            print("------------")
            for x in listy:
                print(x)


            for sid,dist in positions:
                genome, chrom, refpos = ref_positions[sid][0]
            
            print_result2(sid, genome, chrom, min, mindist, max, maxdist)


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
