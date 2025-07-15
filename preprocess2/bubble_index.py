from intervaltree import IntervalTree
from collections import defaultdict

class Bubble:
    def __init__(self, bubble_data):
        self.id = bubble_data["id"]
        self.range = None
        ref_range =bubble_data["range"]
        if len(ref_range) == 1:
            self.range = [ref_range[0], ref_range[0]]
        elif len(ref_range) == 2:
            self.range = ref_range

        self.inside = bubble_data["inside"]
        self.chain = bubble_data["chain"]
        self.parent = bubble_data["parent"]
        self.children = bubble_data["children"]
        self._siblings = bubble_data["siblings"] # (sib_id, node_id)

    def get_siblings(self):
        return [sib for sib, _ in self._siblings]
    
    def contains(self, id1, id2):
        lower, upper = sorted((id1, id2))
        if len(self.range) == 0:
            return False
        elif len(self.range) == 1:
            return self.range[0] <= lower and self.range[0] >= upper
        else:
            return self.range[0] <= lower and self.range[1] >= upper
    def is_ref(self):
        return self.range is not None

    def __str__(self):
        return f"Bubble(id={self.id}, range={self.range}, parent={self.parent}, children={len(self.children)}, siblings={len(self.get_siblings())})"

    def __repr__(self):
        return f"Bubble({self.id}, range={self.range})"
    
class BubbleIndex:
    def __init__(self, graph, bubble_dict):
        self.bubble_dict = bubble_dict
        self.bubbles = {bid: Bubble(bubble) for bid, bubble in bubble_dict.items()}
        self.parent_tree = IntervalTree()
        self.ref_ids = [int(nid) for nid in graph.nodes if graph.nodes[str(nid)].optional_info.get("ref")]

        for bid,bubble in self.bubbles.items():
            if bubble.range and bubble.parent is None:
                start, end = bubble.range
                self.parent_tree[start:end + 1] = bid

    def get_descendant_ids(self, bubble_id):
        bubble = self.bubbles[bubble_id]
        descendants = set()

        def traverse(bubble):
            for sid in bubble.inside:
                descendants.add(sid)
            for child_id in bubble.children:
                traverse(self.bubbles[child_id])

        traverse(bubble)
        return descendants

    def get_top_level_bubbles(self, qstart, qend, as_chains=False):
        results = []

        # Start with all overlapping parentless bubbles
        for iv in self.parent_tree[qstart:qend+1]:
            parent_bubble = self.bubbles[iv.data]
            result = self._traverse_descendants(parent_bubble, qstart, qend)
            results.extend(result)

        non_ref_results = self._collect_non_ref(results)
        results.extend(non_ref_results)

        if as_chains:
            chain_results = defaultdict(list)
            for bubble in results:
                chain_results[bubble.chain].append(bubble)
            return chain_results

        return results

    def _fully_within(self, bubble, qstart, qend):
        return bubble.range[0] >= qstart and bubble.range[1] <= qend

    def _traverse_descendants(self, bubble, qstart, qend):
        # If this bubble is fully contained, return it as a result
        if self._fully_within(bubble, qstart, qend):
            return [bubble]

        # Otherwise, recurse through children
        results = []
        for child_id in bubble.children:
            child = self.bubbles[child_id]
            results.extend(self._traverse_descendants(child, qstart, qend))
        return results

    def _collect_non_ref(self, results, debug=False):
        result_ids = {r.id for r in results}
        visited = set(result_ids)
        collected = set()

        for bubble in results:
            for sib_id in bubble.get_siblings():
                if sib_id in visited:
                    continue
                if self.bubbles[sib_id].is_ref():
                    continue

                component = set()
                stack = [sib_id]
                ref_sources = {bubble.id}

                while stack:
                    curr_id = stack.pop()
                    curr_bubble = self.bubbles[curr_id]

                    if curr_id in result_ids:
                        ref_sources.add(curr_id)
                        continue
                    elif curr_id in visited:
                        continue

                    visited.add(curr_id)

                    if not curr_bubble.is_ref():
                        component.add(curr_id)
                        
                        for sib_id in curr_bubble.get_siblings():
                                stack.append(sib_id)

                if len(ref_sources) >= 2:
                    if debug:
                        print(f"[DEBUG] Recovered component with {len(component)} non-ref bubbles, ref sources: {ref_sources}")

                    for cid in component:
                        if cid not in collected:
                            collected.add(cid)
                            results.append(self.bubbles[cid])
        return [self.bubbles[cid] for cid in collected]

