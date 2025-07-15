import csv
from collections import defaultdict

def parse_gfa(gfa_path):
    segments = []
    adjacency = defaultdict(set)

    index = 0
    with open(gfa_path, 'r') as f:
        for line in f:
            if line.startswith('S'):
                parts = line.strip().split('\t')
                seg_id = parts[1]
                segments.append(seg_id)
                index += 1
            elif line.startswith('L'):
                parts = line.strip().split('\t')
                from_id = parts[1]
                to_id = parts[3]
                adjacency[from_id].add(to_id)
                adjacency[to_id].add(from_id)

    return segments, dict(adjacency)

def parse_layout_file(layout_path):
    layout = {}
    with open(layout_path, newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            idx = int(row['idx'])
            x = float(row['X'])
            y = float(row['Y'])
            layout[idx] = (x, y)
    return layout

def coordinate_map(segments, layout):
    segment_coords = {}
    for i, seg_id in enumerate(segments):
        start_coord = layout.get(2 * i)
        end_coord = layout.get(2 * i + 1)
        if start_coord is not None and end_coord is not None:
            segment_coords[seg_id] = [start_coord, end_coord]
    return segment_coords

def parse_layout_file_coords(layout_path):
    layout_coords = []
    with open(layout_path, newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            idx = int(row['idx'])
            x = float(row['X'])
            y = float(row['Y'])
            layout_coords.append([x, y])
    return layout_coords


def line_pairs(layout_coords):
    lines = []
    num_pairs = len(layout_coords) // 2
    for i in range(num_pairs):
        start_coord = layout_coords[2 * i]
        end_coord = layout_coords[2 * i + 1]
        lines.append([start_coord, end_coord])
    return lines



def line_pairs_w_links(layout_coords):
    lines = []
    for i in range(len(layout_coords) - 1):
        start_coord = layout_coords[i]
        end_coord = layout_coords[i + 1]
        lines.append([start_coord, end_coord])
    return lines
