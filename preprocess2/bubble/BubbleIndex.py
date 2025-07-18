import os
from intervaltree import IntervalTree
from collections import defaultdict
from preprocess2.bubble.bubble_index_utils import NAME, load_bubbles_from_json
import math


class BubbleIndex:
    def __init__(self, chr_dir):
        filepath = os.path.join(chr_dir, NAME)
        bubbles = load_bubbles_from_json(filepath)

        self.bubble_dict = {bubble.id: bubble for bubble in bubbles}
        self.parent_tree = IntervalTree()

        for bubble in bubbles:
            if bubble.has_range(exclusive=False) and (bubble.parent is None):
                for start,end in bubble.get_ranges(exclusive=False):
                    self.parent_tree[start:end + 1] = bubble.id

    def __getitem__(self, bubble_id):
        return self.bubble_dict[bubble_id]
    
    def containing_segment(self, seg_id):
        matching_bubbles = []

        for bubble in self.bubble_dict.values():
            seg_ids = list(bubble.inside)
            if seg_id in seg_ids:
                matching_bubbles.append(bubble)

        return matching_bubbles

    def get_top_level_bubbles(self, min_step, max_step, as_chains=False):
        results = []

        # Start with all overlapping parentless bubbles
        for iv in self.parent_tree[min_step:max_step+1]:
            parent_bubble = self.bubble_dict[iv.data]
            result = self._traverse_descendants(parent_bubble, min_step, max_step)

            results.extend(result)

        non_ref_results = self._collect_non_ref(results)
        results.extend(non_ref_results)

        if as_chains:
            chain_results = defaultdict(list)
            for bubble in results:
                chain_results[bubble.chain].append(bubble)
            return chain_results

        return results

    def _traverse_descendants(self, bubble, min_step, max_step):
        if bubble.is_contained(min_step, max_step):
            return [bubble]
        # Otherwise, recurse through children
        results = []
        for child_id in bubble.children:
            child = self.bubble_dict[child_id]
            results.extend(self._traverse_descendants(child, min_step, max_step))
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

    def get_merged_intervals(self, bubbles, min_step=-1, max_step=math.inf):
        bubble_intervals = []

        for bubble in bubbles:
            for lo, hi in bubble.get_ranges(exclusive=False):
                if hi < min_step or lo > max_step:
                    continue

                lo = max(lo, min_step) if min_step != -1 else lo
                hi = min(hi, max_step) if max_step != math.inf else hi

                bubble_intervals.append((lo, hi))

        bubble_intervals.sort(key=lambda x: x[0])
        merged = []

        for interval in bubble_intervals:
            if not merged:
                merged.append(interval)
            else:
                last_start, last_end = merged[-1]
                curr_start, curr_end = interval

                if curr_start <= last_end + 1:
                    merged[-1] = (last_start, max(last_end, curr_end))
                else:
                    merged.append(interval)

        return merged

