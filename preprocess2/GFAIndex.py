from collections import deque
from dataclasses import dataclass

base_to_bits = {'A': 0b00, 'C': 0b01, 'G': 0b10, 'T': 0b11}

@dataclass(slots=True)
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

    def bfs_subgraph(self, start_id, end_id):
        # Constraint: cannot traverse through reference nodes that are
        #    *outside* the range between start_id and end_id.

        def constrained_bfs(start_id, end_id):
            min_id = min(start_id, end_id)
            max_id = max(start_id, end_id)
            visited = set()
            queue = deque([start_id])
            visited.add(start_id)

            while queue:
                current = queue.popleft()
                for neighbor in self.get_neighbors(current, direction=None):
                    if neighbor in visited:
                        continue
                    seg = self.segments[neighbor]
                    if seg["ref"] and not (min_id <= seg["id"] <= max_id):
                        continue
                    visited.add(neighbor)
                    queue.append(neighbor)
            return visited

        forward_subgraph = constrained_bfs(start_id, end_id)
        if end_id in forward_subgraph:
            return forward_subgraph
        
        # Fallback: reverse BFS
        reverse_subgraph = constrained_bfs(end_id, start_id)

        return forward_subgraph | reverse_subgraph
