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

        if len(subgraph["graph"]) > 0:
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

def compute_bubble_properties(graph, bubble):
    
    inside_nodes = [graph.nodes[nid] for nid in [n.id for n in bubble.inside]]
    lengths = [n.seq_len for n in inside_nodes]
    gc_counts = [n.optional_info.get("gc_count", 0) for n in inside_nodes]

    properties = {
        "length": sum(lengths),
        "largest_child": max(lengths),
        "children": len(inside_nodes),
        "gc_count": sum(gc_counts),
        "ref": any(n.optional_info.get("ref") for n in inside_nodes)
    }

    left_node = graph.nodes[bubble.source.id]
    right_node = graph.nodes[bubble.sink.id]

    left_chrom = left_node.optional_info.get("chrom")
    right_chrom = right_node.optional_info.get("chrom")
    left_genome = left_node.optional_info.get("genome")
    right_genome = right_node.optional_info.get("genome")

    chrom = left_chrom if left_chrom is not None else right_chrom
    genome = left_genome if left_genome is not None else right_genome
    
    if chrom is None or genome is None:
        return properties

    if left_chrom is not None and right_chrom is not None and left_chrom != right_chrom:
        print(f"⚠️ WARNING: Bubble {bubble.id} spans chromosomes: {left_chrom} → {right_chrom}")
        return properties

    if left_genome is not None and right_genome is not None and left_genome != right_genome:
        print(f"⚠️ WARNING: Bubble {bubble.id} spans genomes: {left_genome} → {right_genome}")
        return properties

    left_pos = left_node.optional_info.get("end")
    right_pos = right_node.optional_info.get("start")

    flipped = False
    if left_pos is not None and right_pos is not None and left_pos > right_pos:
        left_node, right_node = right_node, left_node
        left_pos = left_node.optional_info.get("end")
        right_pos = right_node.optional_info.get("start")
        flipped = True

    bubble_left, bubble_right = None, None
    if left_pos is not None and right_pos is not None:
        bubble_left = left_pos + 1
        bubble_right = right_pos - 1

    inside_starts = [n.optional_info.get("start") for n in inside_nodes if n.optional_info.get("ref")]
    inside_ends = [n.optional_info.get("end") for n in inside_nodes if n.optional_info.get("ref")]
    inside_left = min(inside_starts) if inside_starts else None
    inside_right = max(inside_ends) if inside_ends else None

    left, right = None, None
    if bubble_left is not None:
         left, right = bubble_left, bubble_right
    elif inside_left is not None and inside_right is not None:
        left, right = inside_left, inside_right

    properties.update({
        "start": left,
        "end": right,
        "chrom": chrom,
        "genome": genome,
    })

    return properties


def compute_chain_properties(graph, chain, chain_bubbles):
    
    first_bubble = chain_bubbles[0]
    last_bubble = chain_bubbles[-1]

    left_node = graph.nodes[first_bubble.source.id]
    right_node = graph.nodes[last_bubble.sink.id]

    # Flatten segments from all bubbles in the chain
    inside_ids = set()
    for bubble in chain_bubbles:
        inside_ids.update(seg.id for seg in bubble.inside)
        inside_ids.add(bubble.source.id)
        inside_ids.add(bubble.sink.id)

    inside_ids.discard(left_node.id)
    inside_ids.discard(right_node.id)

    inside_nodes = [graph.nodes[nid] for nid in inside_ids]

    lengths = [n.seq_len for n in inside_nodes]
    gc_counts = [n.optional_info.get("gc_count", 0) for n in inside_nodes]

    properties = {
        "length": sum(lengths),
        "largest_child": max(lengths),
        "children": len(inside_nodes),
        "gc_count": sum(gc_counts),
        "ref": any(n.optional_info.get("ref") for n in inside_nodes)
    }

    left_chrom = left_node.optional_info.get("chrom")
    right_chrom = right_node.optional_info.get("chrom")
    left_genome = left_node.optional_info.get("genome")
    right_genome = right_node.optional_info.get("genome")

    chrom = left_chrom if left_chrom is not None else right_chrom
    genome = left_genome if left_genome is not None else right_genome

    if chrom is None or genome is None:
        return properties

    if left_chrom is not None and right_chrom is not None and left_chrom != right_chrom:
        print(f"⚠️ WARNING: Chain {chain.id} spans chromosomes: {left_chrom} → {right_chrom}")
        return properties

    if left_genome is not None and right_genome is not None and left_genome != right_genome:
        print(f"⚠️ WARNING: Chain {chain.id} spans genomes: {left_genome} → {right_genome}")
        return properties

    left_pos = left_node.optional_info.get("end")
    right_pos = right_node.optional_info.get("start")

    flipped = False
    if left_pos is not None and right_pos is not None and left_pos > right_pos:
        left_node, right_node = right_node, left_node
        left_pos = left_node.optional_info.get("end")
        right_pos = right_node.optional_info.get("start")
        flipped = True

    chain_left = left_pos if left_pos is not None else None
    chain_right = right_pos if right_pos is not None else None

    inside_starts = [n.optional_info.get("start") for n in inside_nodes if n.optional_info.get("ref")]
    inside_ends = [n.optional_info.get("end") for n in inside_nodes if n.optional_info.get("ref")]
    inside_left = min(inside_starts) if inside_starts else None
    inside_right = max(inside_ends) if inside_ends else None

    left, right = None, None
    if chain_left is not None:
        left, right = chain_left, chain_right
    elif inside_left is not None and inside_right is not None:
        left, right = inside_left, inside_right

    properties.update({
        "start": left,
        "end": right,
        "chrom": chrom,
        "genome": genome,
    })

    return properties
    
def propagate_optional_info(graph, merged_map, original_info):
    for compacted_id, original_ids in merged_map.items():
        original_infos = [original_info[oid] for oid in original_ids if oid in original_info]

        if compacted_id in original_info:
            original_infos.append(original_info[compacted_id])

        if not original_infos:
            continue

        genomes = {info.get("genome") for info in original_infos if info.get("genome") is not None}
        chroms = {info.get("chrom") for info in original_infos if info.get("chrom") is not None}
        starts = [info.get("start") for info in original_infos if info.get("start") is not None]
        ends = [info.get("end") for info in original_infos if info.get("end") is not None]
        gc_total = sum(info.get("gc_count", 0) for info in original_infos)
        ref = any(info.get("ref") for info in original_infos)

        genome = genomes.pop() if len(genomes) == 1 else None
        chrom = chroms.pop() if len(chroms) == 1 else None
        start = min(starts) if starts else None
        end = max(ends) if ends else None

        graph.nodes[compacted_id].optional_info = {
            "genome": genome,
            "chrom": chrom,
            "start": start,
            "end": end,
            "ref": ref,
            "gc_count": gc_total
        }
