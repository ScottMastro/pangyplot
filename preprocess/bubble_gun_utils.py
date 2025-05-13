from collections import deque

def assign_bubble_depths(bubble_dict, child_bubbles):
    nesting_cache = {}
    depth_cache = {}

    def get_nesting_level(bid):
        if bid in nesting_cache:
            return nesting_cache[bid]
        bubble = bubble_dict.get(bid)
        if not bubble or not bubble.parent_sb:
            nesting_cache[bid] = 0
            return 0
        level = 1 + get_nesting_level(bubble.parent_sb)
        nesting_cache[bid] = level
        return level

    def get_depth_below(bid):
        if bid in depth_cache:
            return depth_cache[bid]
        children = child_bubbles.get(bid, [])
        if not children:
            depth = 0
        else:
            depth = 1 + max(get_depth_below(child.id) for child in children)
        depth_cache[bid] = depth
        return depth

    bubble_metadata = {}
    for bid, _ in bubble_dict.items():
        bubble_metadata[bid] = {
            "nesting_level": get_nesting_level(bid),
            "depth": get_depth_below(bid),
        }

    return bubble_metadata

def bfs_find_subgraph(graph, start_node):
    queue = deque([start_node])
    visited = set()
    refset = set()

    while queue:
        
        current = queue.popleft()

        if current.optional_info["ref"]:
            refset.add(current.id)
            continue

        if current.id in visited:
            continue

        visited.add(current.id)

        for neighbor in current.neighbors():
            if neighbor not in visited:
                queue.append(graph.nodes[neighbor])

    return {"anchor": refset, "graph": visited}

def create_alt_subgraphs(graph):
    nodes = list(graph.nodes.keys())
    visited = set()
    subgraphs = []
    for nid in nodes:
        node = graph.nodes[nid]
        if nid in visited:
            continue
        if node.optional_info["ref"]:
            visited.add(nid)
            continue
        
        subgraph = bfs_find_subgraph(graph, node)
        for v in subgraph["graph"]:
            visited.add(v)

        if len(subgraph["graph"]) > 1:
            subgraphs.append(subgraph)

    return subgraphs

def score_orientation(graph, bubble):
    inside_ids = {n.id for n in bubble.inside}
    source = graph.nodes[bubble.source.id]
    sink = graph.nodes[bubble.sink.id]

    score = 0

    # ✅ Favor: source.end → inside
    for neighbor_id, dir, _ in source.end:
        if neighbor_id in inside_ids:
            score += 1

    # ❌ Penalize: source.start → inside
    for neighbor_id, dir, _ in source.start:
        if neighbor_id in inside_ids:
            score -= 1

    # ✅ Favor: sink.start → inside
    for neighbor_id, dir, _ in sink.start:
        if neighbor_id in inside_ids:
            score += 1

    # ❌ Penalize: sink.end → inside
    for neighbor_id, dir, _ in sink.end:
        if neighbor_id in inside_ids:
            score -= 1

    return score

def normalize_bubble_direction(graph, bubble):
    original_score = score_orientation(graph, bubble)

    # Try flipped version
    bubble.source, bubble.sink = bubble.sink, bubble.source
    flipped_score = score_orientation(graph, bubble)

    if flipped_score > original_score:
        pass
    else: # flip back
        bubble.source, bubble.sink = bubble.sink, bubble.source


def normalize_chain_direction(graph, bubble_list):
    score = 0
    for i in range(len(bubble_list) - 1):
        b1 = bubble_list[i]
        b2 = bubble_list[i+1]

        # ✅ Favor: b1.sink is b2.source (i.e., bubbles are chained)
        if b1.sink.id == b2.source.id:
            score += 1

        # ❌ Penalize: backward chain — b2.sink precedes b1.source
        if b2.sink.id == b1.source.id:
            score -= 1

    if score < 0:
        bubble_list.reverse()


def split_chain(chain, max_bubbles=100):
    if not chain.sorted:
        chain.sort()
    bubbles = chain.sorted
    
    n = len(bubbles)
    if n <= max_bubbles:
        return [bubbles]

    num_chunks = (n + max_bubbles - 1) // max_bubbles
    chunk_size = n // num_chunks
    remainder = n % num_chunks

    chunks = []
    start = 0
    for i in range(num_chunks):
        end = start + chunk_size + (1 if i < remainder else 0)
        chunks.append(bubbles[start:end])
        start = end

    return chunks
