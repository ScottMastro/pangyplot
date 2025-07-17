from collections import deque
from dataclasses import dataclass

base_to_bits = {'A': 0b00, 'C': 0b01, 'G': 0b10, 'T': 0b11}

@dataclass
class Link:
    from_id: int
    from_strand: str  # '+' or '-'
    to_id: int
    to_strand: str
    haplotype: int     # store as int, not hex string
    frequency: float
    ref: bool

def encode_seq(seq):
    encoded = bytearray((len(seq) + 3) // 4)
    for i, base in enumerate(seq):
        bits = base_to_bits.get(base, 0b00)  # N defaults to A (00)
        encoded[i // 4] |= bits << (6 - 2 * (i % 4))
    return bytes(encoded)

bits_to_base = ['A', 'C', 'G', 'T']

def decode_seq(encoded, length):
    seq = []
    for i in range(length):
        byte = encoded[i // 4]
        bits = (byte >> (6 - 2 * (i % 4))) & 0b11
        seq.append(bits_to_base[bits])
    return ''.join(seq)


class GFAIndex:
    def __init__(self, segments, links, sample_idx):
        self.segments = segments
        self.links = []
        self.sample_idx = sample_idx

        self.forward_index = dict()
        self.reverse_index = dict()

        for _,link in links.items():
            link_obj = Link(
                from_id=link["from_id"],
                from_strand=link["from_strand"],
                to_id=link["to_id"],
                to_strand=link["to_strand"],
                haplotype=int(link["haplotype"], 16),
                frequency=link["frequency"],
                ref=link["ref"])
            self.links.append(link_obj)


        for (fid, tid), _ in links.items():
            if fid not in self.forward_index:
                self.forward_index[fid] = []
            if tid not in self.reverse_index:
                self.reverse_index[tid] = []
            self.forward_index[fid].append(tid)
            self.reverse_index[tid].append(fid)

    def __getitem__(self, segment_id):
        return self.segments[segment_id]

    def get_links(self, segment_id):
        links = []

        for neighbor_id in self.forward_index.get(segment_id, []):
            link = self.links.get((segment_id, neighbor_id))
            if link:
                links.append(link)

        for neighbor_id in self.reverse_index.get(segment_id, []):
            link = self.links.get((neighbor_id, segment_id))
            if link:
                links.append(link)

        return links

    def get_neighbors(self, segment_id, direction=None):
        if direction is None:
            return list(set(self.forward_index.get(segment_id, []) + 
                            self.reverse_index.get(segment_id, [])))
        elif direction == '+':
            return self.forward_index.get(segment_id, [])
        elif direction == '-':
            return self.reverse_index.get(segment_id, [])
        elif direction is None:
            return list(set(self.forward_index.get(segment_id, []) + 
                            self.reverse_index.get(segment_id, [])))
        else:
            raise ValueError("Direction must be '+', '-', or None")

    def get_haplotype_presence(self, link, sample_name):
        #todo: test and verify
        if isinstance(link, tuple):
            link = self.get_link(*link)
        if not link:
            return False
        hap_str = link.get("haplotype", "0")
        hap_int = int(hap_str, 16)
        sample_idx = self.sample_idx.get(sample_name)
        if sample_idx is None:
            return False
        return ((hap_int >> sample_idx) & 1) == 1

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
            
            start_seg_id = step_index.get_segment(seed_step)
            if start_seg_id is None:
                raise ValueError(f"No segment found for start_step {seed_step}")

            queue.append(start_seg_id)
            visited.add(start_seg_id)

            while queue:
                current = queue.popleft()
                for neighbor in self.get_neighbors(current, direction=None):
                    if neighbor in visited:
                        continue

                    steps = step_index[neighbor]
                    if not any(min_step <= s <= max_step for s in steps):
                        continue

                    visited.add(neighbor)
                    queue.append(neighbor)

            return visited

        # Try forward BFS
        forward_visited = constrained_bfs(start_step, end_step)

        # Check if end_step is reached
        end_seg_id = step_index.get_segment(end_step)
        if end_seg_id is not None and end_seg_id in forward_visited:
            return forward_visited

        # Fallback: reverse BFS
        reverse_visited = constrained_bfs(end_step, start_step)

        return forward_visited | reverse_visited
    
    def filter_ref(self, seg_ids, ref=True):
        return [sid for sid in seg_ids if self.segments[sid]["ref"] == ref]

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
        """
        Export the BFS subgraph from `start_id` up to `max_steps` steps to a GFA file.
        Only segments and links are included (no paths).
        """
        visited = self.bfs_steps(start_id, max_steps)
        visited = set(visited)

        with open(save_path, 'w') as f:
            f.write("H\tVN:Z:1.0\n")

            for node_id in visited:
                seg = self.segments[node_id]
                seq = seg.get("sequence", "N")  # fallback if no sequence
                f.write(f"S\t{node_id}\t{seq}\n")

            # Write links
            for link in self.links:
                if link.from_id in visited and link.to_id in visited:
                    f.write(f"L\t{link.from_id}\t{link.from_strand}\t{link.to_id}\t{link.to_strand}\t0M\n")

        print(f"✅ Exported GFA subgraph to: {save_path}")
