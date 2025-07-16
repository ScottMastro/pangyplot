from intervaltree import IntervalTree
from collections import defaultdict
    
class BubbleIndex:
    def __init__(self, bubbles):
        self.bubble_dict = {bubble.id: bubble for bubble in bubbles}
        self.parent_tree = IntervalTree()

        for bubble in bubbles:
            if bubble.range and (bubble.parent is None):
                start, end = bubble.range
                self.parent_tree[start:end + 1] = bubble.id

    def get_top_level_bubbles(self, qstart, qend, as_chains=False):
        results = []

        # Start with all overlapping parentless bubbles
        for iv in self.parent_tree[qstart:qend+1]:
            parent_bubble = self.bubble_dict[iv.data]
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
            child = self.bubble_dict[child_id]
            results.extend(self._traverse_descendants(child, qstart, qend))
        return results

    def get_sibling_segments(self, bubbles, inside_only=False):
        sibling_segments = defaultdict(int)
        for bubble in bubbles:
            for node_id in bubble.get_sibling_segments():
                sibling_segments[node_id] += 1
        
        if inside_only:
            return {nid for nid, count in sibling_segments.items() if count > 1}
        else:
            return {nid for nid, _ in sibling_segments.items()}

    def get_descendant_ids(self, bubble):
        descendants = set()

        def traverse(bubble):
            for sid in bubble.inside:
                descendants.add(sid)
            for child_id in bubble.children:
                traverse(self.bubble_dict[child_id])

        traverse(bubble)
        return descendants

    def _collect_non_ref(self, results, debug=False):
        result_bubbles = set(results)
        visited = set(result_bubbles)
        collected = set()

        for bubble in results:
            for sib_id in bubble.get_siblings():
                sib = self.bubble_dict[sib_id]
                if sib.is_ref() or sib in visited:
                    continue
                
                component = set()
                stack = [sib]
                ref_sources = {bubble}

                while stack:
                    curr_bubble = stack.pop()

                    if curr_bubble in result_bubbles:
                        ref_sources.add(curr_bubble)
                        continue
                    elif curr_bubble in visited:
                        continue

                    visited.add(curr_bubble)

                    if not curr_bubble.is_ref():
                        component.add(curr_bubble)
                        for sib_id in bubble.get_siblings():
                            stack.append(self.bubble_dict[sib_id])

                if len(ref_sources) >= 2:
                    if debug:
                        print(f"[DEBUG] Recovered component with {len(component)} non-ref bubbles, ref sources: {[b.id for b in ref_sources]}")

                    for b in component:
                        if b not in collected:
                            collected.add(b)
                            results.append(b)

        return list(collected)

