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

        self.ends = [int(raw_bubble.source.id), int(raw_bubble.sink.id)]
        compacted_ends = [int(compacted_dict[end].id) for end in self.ends if end in compacted_dict]
        self.ends.extend(compacted_ends)

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
    def get_sibling_segments(self):
        return [seg_id for _, seg_id in self._siblings]

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
        return f"Bubble(id={self.id}, range={self.range}, parent={self.parent}, children={len(self.children)}, siblings={len(self.get_siblings())})"

    def __repr__(self):
        return f"Bubble({self.id}, range={self.range})"
