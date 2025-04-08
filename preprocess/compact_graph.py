# Modified from the BubbleGun source code to track merges.

from collections import defaultdict

def merge_node(graph, n_id, direction="forward", merged_map=None):
    nodes = graph.nodes
    node = nodes[n_id]

    neighbors = node.end if direction == "forward" else node.start
    if len(neighbors) != 1:
        return False

    [neighbor] = neighbors
    neighbor_id = neighbor[0]
    if n_id == neighbor_id:
        return False  # skip self-loops

    neighbor_node = nodes[neighbor_id]
    neighbor_side = neighbor[1]  # 0: start, 1: end

    if direction == "forward":
        if neighbor_side == 0 and len(neighbor_node.start) == 1:
            new_neighbors = list(neighbor_node.end)
        elif neighbor_side == 1 and len(neighbor_node.end) == 1:
            new_neighbors = list(neighbor_node.start)
        else:
            return False

        node.end.update(new_neighbors)
        node.seq = ""
        node.seq_len = 0

    elif direction == "backward":
        if neighbor_side == 1 and len(neighbor_node.end) == 1:
            new_neighbors = list(neighbor_node.start)
        elif neighbor_side == 0 and len(neighbor_node.start) == 1:
            new_neighbors = list(neighbor_node.end)
        else:
            return False

        node.start.update(new_neighbors)
        node.seq = ""
        node.seq_len = 0

    # Track merged node
    if merged_map is not None:
        merged_map[n_id].append(neighbor_id)
        merged_map[n_id].extend(merged_map.get(neighbor_id, []))

    graph.remove_node(neighbor_id)

    for nn in new_neighbors:
        target_id = nn[0]
        overlap = nn[2]

        if direction == "forward":
            if nn[1] == 0:
                graph.nodes[target_id].start.add((n_id, 1, overlap))
            else:
                if target_id != neighbor_id:
                    graph.nodes[target_id].end.add((n_id, 1, overlap))
                else:
                    node.end.discard((neighbor_id, 1, overlap))
                    node.end.add((n_id, 1, overlap))
        else:
            if nn[1] == 0:
                if target_id != neighbor_id:
                    graph.nodes[target_id].start.add((n_id, 0, overlap))
                else:
                    node.start.discard((neighbor_id, 0, overlap))
                    node.start.add((n_id, 0, overlap))
            else:
                graph.nodes[target_id].end.add((n_id, 0, overlap))

    return True


def compact_graph(graph):
    merged_map = defaultdict(list)

    node_ids = list(graph.nodes.keys())
    for n in node_ids:
        if n not in graph.nodes:
            continue

        while merge_node(graph, n, direction="forward", merged_map=merged_map):
            pass
        while merge_node(graph, n, direction="backward", merged_map=merged_map):
            pass

    # Final cleanup: deduplicate and sort lists
    for compacted_id in merged_map:
        merged_map[compacted_id] = sorted(set(merged_map[compacted_id]))

    return merged_map
