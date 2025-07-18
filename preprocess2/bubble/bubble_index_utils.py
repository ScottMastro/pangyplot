import gzip
import json
import os
from collections import defaultdict
from preprocess2.bubble.BubbleData import BubbleData

NAME="bubble_index.json.gz"

def find_siblings(bubbles):
    sib_dict = defaultdict(set)
    
    for bubble in bubbles:
        for sid in bubble.get_sibling_segments():
            sib_dict[sid].add(bubble)

    for bubble in bubbles:
        for sid in bubble.get_sibling_segments():
            for sibling in sib_dict[sid]:
                if sibling.id != bubble.id:
                    bubble.add_sibling(sibling.id, sid)

def find_parent_children(bubbles):
    bubble_dict = {bubble.id: bubble for bubble in bubbles}

    for bubble in bubbles:
        if bubble.parent:
            bubble_parent = bubble_dict[bubble.parent]
            bubble_parent.add_child(bubble, bubble_dict)

def find_siblings(bubbles):
    sib_dict = defaultdict(set)
    
    for bubble in bubbles:
        for sid in bubble.get_sibling_segments():
            sib_dict[sid].add(bubble)

    for bubble in bubbles:
        for sid in bubble.get_sibling_segments():
            for sibling in sib_dict[sid]:
                if sibling.id != bubble.id:
                    bubble.add_sibling(sibling.id, sid)

def find_parent_children(bubbles):
    bubble_dict = {bubble.id: bubble for bubble in bubbles}

    for bubble in bubbles:
        if bubble.parent:
            bubble_parent = bubble_dict[bubble.parent]
            bubble_parent.add_child(bubble, bubble_dict)

def create_bubble_object(raw_bubble, chain_id, step_index):
    bubble = BubbleData()

    bubble.id = f"b{raw_bubble.id}"
    bubble.chain = chain_id

    if raw_bubble.is_insertion():
        bubble.type = "insertion"
    elif raw_bubble.is_super():
        bubble.type = "super"

    bubble.parent = f"b{raw_bubble.parent_sb}" if raw_bubble.parent_sb else None

    # Source and sink
    source_node = raw_bubble.source
    bubble._source = int(source_node.id)
    compacted_source_nodes = list(source_node.optional_info.get("compacted", []))
    bubble._compacted_source = [int(node.id) for node in compacted_source_nodes]

    sink_node = raw_bubble.sink
    bubble._sink = int(sink_node.id)
    compacted_sink_nodes = list(sink_node.optional_info.get("compacted", []))
    bubble._compacted_sink = [int(node.id) for node in compacted_sink_nodes]

    # Inside nodes + compacted
    nodes = raw_bubble.inside
    compacted_dict = defaultdict(list)
    for node in nodes:
        if node.optional_info.get("compacted"):
            compacted_dict[int(node.id)].extend(node.optional_info["compacted"])
    compacted_nodes = [n for nodes in compacted_dict.values() for n in nodes]

    bubble.inside = {int(n.id) for n in nodes + compacted_nodes}

    # Step range
    def get_steps(seg_ids):
        steps = set()
        for sid in seg_ids:
            steps.update(step_index[sid])
        return steps

    inside_steps = get_steps(bubble.inside)
    source_steps = get_steps([int(n.id) for n in [source_node] + compacted_source_nodes])
    sink_steps = get_steps([int(n.id) for n in [sink_node] + compacted_sink_nodes])

    def collapse_ranges(steps):
        if not steps:
            return []

        sorted_steps = sorted([int(s) for s in steps])
        ranges = []
        start = prev = sorted_steps[0]

        for step in sorted_steps[1:]:
            if step == prev + 1:
                prev = step
            else:
                ranges.append((start, prev))
                start = prev = step

        ranges.append((start, prev))
        return ranges

    bubble._range_exclusive = collapse_ranges(inside_steps)
    bubble._range_inclusive = collapse_ranges(inside_steps.union(source_steps, sink_steps))

    # Length and base content
    bubble.length = sum(n.seq_len for n in nodes)
    bubble.gc_count = sum(n.optional_info.get("gc_count", 0) for n in nodes)
    bubble.n_counts = sum(n.optional_info.get("n_count", 0) for n in nodes)

    return bubble

def bubble_to_dict(bubble):
    return {
        "id": bubble.id,
        "chain": bubble.chain,
        "type": bubble.type,
        "parent": bubble.parent,
        "children": bubble.children,
        "_siblings": bubble._siblings,
        "_source": bubble._source,
        "_compacted_source": bubble._compacted_source,
        "_sink": bubble._sink,
        "_compacted_sink": bubble._compacted_sink,
        "inside": list(bubble.inside),
        "_range_exclusive": bubble._range_exclusive,
        "_range_inclusive": bubble._range_inclusive,
        "length": bubble.length,
        "gc_count": bubble.gc_count,
        "n_counts": bubble.n_counts,
    }

def write_bubbles_to_json(bubbles, chr_dir):
    filepath = os.path.join(chr_dir, NAME)
    with gzip.open(filepath, 'wt') as f:
        json.dump([bubble_to_dict(b) for b in bubbles], f)

def dict_to_bubble(d):
    bubble = BubbleData()
    bubble.id = d["id"]
    bubble.chain = d["chain"]
    bubble.type = d["type"]
    bubble.parent = d["parent"]
    bubble.children = d["children"]
    bubble._siblings = d["_siblings"]
    bubble._source = d["_source"]
    bubble._compacted_source = d["_compacted_source"]
    bubble._sink = d["_sink"]
    bubble._compacted_sink = d["_compacted_sink"]
    bubble.inside = set(d["inside"])
    bubble._range_exclusive = d["_range_exclusive"]
    bubble._range_inclusive = d["_range_inclusive"]
    bubble.length = d["length"]
    bubble.gc_count = d["gc_count"]
    bubble.n_counts = d["n_counts"]
    return bubble

def load_bubbles_from_json(filepath):
    with gzip.open(filepath, 'rt') as f:
        data = json.load(f)
        return [dict_to_bubble(d) for d in data]


