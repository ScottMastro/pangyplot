from collections import deque
from dataclasses import dataclass
from preprocess2.gfa.data_structures.LinkIndex import LinkIndex
from preprocess2.gfa.data_structures.SegmentIndex import SegmentIndex


class GFAIndex:
    def __init__(self, db_dir):
        self.segment_index = SegmentIndex(db_dir)
        self.link_index = LinkIndex(db_dir)

    def __getitem__(self, segment_id):
        return self.segments[segment_id]

    def get_links(self, seg_id):
        return self.link_index[seg_id]

    def get_neighbors(self, seg_id, direction=None):
        neighbors = []

        for link in self.link_index[seg_id]:
            if link["from_id"] == seg_id:
                strand = link["from_strand"]
                neighbor = link["to_id"]
                dir_label = '+'  # going forward
            else:
                strand = link["to_strand"]
                neighbor = link["from_id"]
                dir_label = '-'  # coming backward

            if direction is None or direction == dir_label:
                neighbors.append(neighbor)

        return neighbors

    def traverse(self, start_id, max_steps=10, direction=None):
        path = [start_id]
        current = start_id
        for _ in range(max_steps):
            neighbors = self.get_neighbors(current, direction)
            if not neighbors:
                break
            current = neighbors[0]
            path.append(current)
        return path

    def bfs_subgraph(self, start_step, end_step, step_index):
        # Constraint: cannot traverse through reference nodes that are
        #    *outside* the range between start_step and end_step.
        min_step = min(start_step, end_step)
        max_step = max(start_step, end_step)
        
        def constrained_bfs(seed_step, target_step):
            visited = set()
            queue = deque()
            
            start_seg_id = step_index[seed_step]
            if start_seg_id is None:
                raise ValueError(f"No segment found for start_step {seed_step}")

            queue.append(start_seg_id)
            visited.add(start_seg_id)

            while queue:
                current = queue.popleft()
                for neighbor in self.get_neighbors(current, direction=None):
                    if neighbor in visited:
                        continue

                    steps = step_index.get_steps_for_segment(neighbor)
                    if not any(min_step <= s <= max_step for s in steps):
                        continue

                    visited.add(neighbor)
                    queue.append(neighbor)

            return visited

        # Try forward BFS
        forward_visited = constrained_bfs(start_step, end_step)

        # Check if end_step is reached
        end_seg_id = step_index[end_step]
        if end_seg_id is not None and end_seg_id in forward_visited:
            return forward_visited

        # Fallback: reverse BFS
        reverse_visited = constrained_bfs(end_step, start_step)

        return forward_visited | reverse_visited
    
    def filter_path(self, seg_ids, step_index, on_path=True):
        keep = []
        for sid in seg_ids:
            check = len(step_index.get_steps_for_segment(sid)) > 0
            if check == on_path:
                keep.append(sid)
        return keep

    def bfs_steps(self, start_id, max_steps):
        visited = set([start_id])
        queue = deque([(start_id, 0)])

        while queue:
            current, steps = queue.popleft()
            if steps >= max_steps:
                continue
    
            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, steps + 1))
        
        return visited

    def export_subgraph_to_gfa(self, start_id, save_path, max_steps=10):

        visited = self.bfs_steps(start_id, max_steps)
        visited = set(visited)

        with open(save_path, 'w') as f:
            f.write("H\tVN:Z:1.0\n")
            segments = self.segment_index.get_by_ids(visited, with_seq=True)
            seg_ids = {int(seg['id']) for seg in segments}

            links = set()
            for segment in segments:
                sid = segment['id']
                f.write(f"S\t{sid}\t{segment['seq']}\n")

                seg_links = self.link_index[sid]

                for link in seg_links:
                    if int(link['from_id']) not in seg_ids or int(link['to_id']) not in seg_ids:
                        continue
                    key = (link['from_id'], link['from_strand'], link['to_id'], link['to_strand'])
                    links.add(key)

            for (fr, fs, to, ts) in links:
                f.write(f"L\t{fr}\t{fs}\t{to}\t{ts}\t0M\n")

        print(f"✅ Exported GFA subgraph to: {save_path}")
