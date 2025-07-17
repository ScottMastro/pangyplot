from intervaltree import IntervalTree
from collections import defaultdict
    
class BubbleIndex:
    def __init__(self, bubbles):
        self.bubble_dict = {bubble.id: bubble for bubble in bubbles}
        self.parent_tree = IntervalTree()

        for bubble in bubbles:
            if len(bubble.extended_range)>0 and (bubble.parent is None):
                start, end = bubble.extended_range
                self.parent_tree[start:end + 1] = bubble.id

    def __getitem__(self, bubble_id):
        return self.bubble_dict[bubble_id]
    
    def containing_segment(self, seg_id):
        matching_bubbles = []

        for bubble in self.bubble_dict.values():
            seg_ids = list(bubble.inside)
            seg_ids.extend(bubble.extended_range)
            if seg_id in seg_ids:
                matching_bubbles.append(bubble)

        return matching_bubbles

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
        if len(bubble.range) > 0:
            return bubble.range[0] >= qstart and bubble.range[1] <= qend
        if len(bubble.extended_range) > 0:
            return bubble.extended_range[0] >= qstart and bubble.extended_range[1] <= qend
        
        return False

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
            for sid in bubble.ends(as_list=True):
                descendants.add(sid)
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
                anchors = {bubble}

                while stack:
                    curr_bubble = stack.pop()

                    if curr_bubble in result_bubbles:
                        anchors.add(curr_bubble)
                        continue
                    elif curr_bubble in visited:
                        continue

                    visited.add(curr_bubble)

                    if not curr_bubble.is_ref():
                        component.add(curr_bubble)
                        for sib_id in curr_bubble.get_siblings():
                            stack.append(self.bubble_dict[sib_id])

                if len(anchors) >= 2:
                    if debug:
                        print(f"[DEBUG] Recovered component with {len(component)} non-ref bubbles, anchors: {[b.id for b in anchors]}")

                    for b in component:
                        if b not in collected:
                            collected.add(b)
                            results.append(b)
        
        return list(collected)

    def get_merged_intervals(self, bubbles):
        bubble_intervals = []
        for bubble in bubbles:
            bubble_intervals.append(bubble.extended_range)

        bubble_intervals.sort(key=lambda x: x[0])
        merged = []
        for interval in bubble_intervals:
            if not merged:
                merged.append(interval)
            else:
                last_start, last_end = merged[-1]
                curr_start, curr_end = interval
                if curr_start <= last_end:
                    merged[-1] = (last_start, max(last_end, curr_end))
                else:
                    merged.append(interval)
        return merged
