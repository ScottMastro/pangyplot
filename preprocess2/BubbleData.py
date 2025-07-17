from collections import defaultdict

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
    source_steps = get_steps([n.id for n in [source_node] + compacted_source_nodes])
    sink_steps = get_steps([n.id for n in [sink_node] + compacted_sink_nodes])

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

class BubbleData:
    def __init__(self):
        self.id = None
        self.chain = None
        self.type = "simple"
        self.parent = None
        self.children = []
        self._siblings = []

        self._source = None
        self._compacted_source = []
        self._sink = None
        self._compacted_sink = []

        self.inside = set()
        self._range_exclusive = []
        self._range_inclusive = []

        self.length = 0
        self.gc_count = 0
        self.n_counts = 0

        self._height = None
        self._depth = None


    def add_sibling(self, sibling_id, segment_id):
        self._siblings.append((sibling_id, segment_id))

    def _clean_inside(self, inside_ids, bubble_dict):
        self.inside -= inside_ids
        if self.parent:
            parent_bubble = bubble_dict.get(self.parent)
            parent_bubble._clean_inside(inside_ids, bubble_dict)

    def add_child(self, child, bubble_dict):
        self.children.append(child.id)
        self._clean_inside(child.inside, bubble_dict)

    def get_siblings(self):
        return list({sib_id for sib_id, _ in self._siblings})
    def get_sibling_segments(self, get_compacted_nodes=True):
        return self.get_source(get_compacted_nodes) + self.get_sink(get_compacted_nodes)

    def get_source(self, get_compacted_nodes=True):
        if not get_compacted_nodes:
            return [self._source]

        return [self._source] + self._compacted_source
    
    def get_sink(self, get_compacted_nodes=True):
        if not get_compacted_nodes:
            return [self._sink]
        
        return [self._sink] + self._compacted_sink

    def ends(self, get_compacted=True, as_list=False):
        sources = [self._source]
        sinks = [self._sink]

        if get_compacted:
            sources += self._compacted_source
            sinks += self._compacted_sink        
        if as_list:
            return sources + sinks
        return (sources, sinks)
    
    def has_range(self, exclusive=True):
        if exclusive:
            return len(self._range_exclusive) > 0
        return len(self._range_inclusive) > 0
    
    def get_ranges(self, exclusive=True):
        if exclusive:
            return self._range_exclusive
        return self._range_inclusive
    
    def is_contained(self, start_step, end_step, strict=False):
        strict_check = any(start >= start_step and end <= end_step for start, end in self._range_exclusive)
        if strict or strict_check:
            return strict_check
        return any(start >= start_step and end <= end_step for start, end in self._range_inclusive)

    def contains(self, id1, id2, exclusive=True):
        lower, upper = sorted((id1, id2))
        if exclusive:
            return any(lo <= lower and hi >= upper for lo, hi in self._range_exclusive)
        return any(lo <= lower and hi >= upper for lo, hi in self._range_inclusive)

    def is_ref(self):
        return len(self._range_inclusive) > 0
    
    def get_height(self):
        if self._height is not None:
            return self._height
        
        if not self.children:
            self._height = 1
        else:
            self._height = 1 + max(child.get_height() for child in self.children)
        
        return self._height
    
    def get_depth(self):
        if self._depth is not None:
            return self._depth
        
        if not self.parent:
            self._depth = 0
        else:
            self._depth = 1 + self.parent.get_depth()
        
        return self._depth

    def __str__(self):
        return f"Bubble(id={self.id}, parent={self.parent}, children={len(self.children)}, siblings={self.get_siblings()}, inside={self.inside}, inclusive range={self._range_inclusive})"

    def __repr__(self):
        return f"Bubble({self.id}, inclusive range={self._range_inclusive})"
