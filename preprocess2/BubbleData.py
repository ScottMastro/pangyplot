from collections import defaultdict

class BubbleData:
    def __init__(self, raw_bubble, chain_id):

        self.id = f"b{raw_bubble.id}"
        self.chain = chain_id

        self.type = "simple"
        if raw_bubble.is_insertion():
            self.type = "insertion"
        elif raw_bubble.is_super():
            self.type = "super"

        self.parent = f"b{raw_bubble.parent_sb}" if raw_bubble.parent_sb else None
        self.children = []
        self._siblings = []
        
        source_node = raw_bubble.source
        self._source = int(source_node.id)
        self._compacted_source = [int(node.id) for node in source_node.optional_info["compacted"]]

        sink_node = raw_bubble.sink
        self._sink = int(sink_node.id)
        self._compacted_sink = [int(node.id) for node in sink_node.optional_info["compacted"]]

        nodes = raw_bubble.inside
                
        compacted_dict = defaultdict(list)
        for node in nodes:
            if node.optional_info.get("compacted"):
                compacted_dict[int(node.id)].extend(node.optional_info["compacted"])

        compacted_nodes = []
        for _, nodes in compacted_dict.items():
            compacted_nodes.extend(nodes)

        self.inside = {int(node.id) for node in nodes+compacted_nodes}
        ref_ids = [int(node.id) for node in nodes if node.optional_info.get("ref")]

        self.range = None
        if len(ref_ids) == 1:
            self.range = [ref_ids[0], ref_ids[0]]
        elif len(ref_ids) > 1:
            self.range = [min(ref_ids), max(ref_ids)]

        self.length = sum([n.seq_len for n in nodes])
        self.gc_count = sum([n.optional_info.get("gc_count", 0) for n in nodes])
        self.n_counts = sum([n.optional_info.get("n_count", 0) for n in nodes])

        self._height = None
        self._depth = None

    def add_sibling(self, sibling_id, segment_id):
        #potentially adjust for compacted nodes here
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
        return [sib_id for sib_id, _ in self._siblings]
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

    def ends(self, get_compacted=True):
        sources = [self._source]
        sinks = [self._sink]

        if get_compacted:
            sources += self._compacted_source
            sinks += self._compacted_sink        
        
        return (sources, sinks)
    
    def contains(self, id1, id2):
        lower, upper = sorted((id1, id2))
        if self.range is None:
            return False
        return self.range[0] <= lower and self.range[1] >= upper
    
    def is_ref(self):
        return self.range is not None
    
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
        return f"Bubble(id={self.id}, range={self.range}, parent={self.parent}, children={len(self.children)}, siblings={self.get_siblings()}, inside={self.inside})"

    def __repr__(self):
        return f"Bubble({self.id}, range={self.range})"
