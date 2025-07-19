import os
import numpy as np
import matplotlib.pyplot as plt
from skimage.draw import line as draw_line
from skimage.morphology import skeletonize
from skimage.transform import resize
from PIL import Image
import preprocess.skeleton.skeleton_layout_parse as parser

### ----------------------------
### Quadtree + Tile Utilities
### ----------------------------

class QuadtreeNode:
    def __init__(self, x0, y0, x1, y1, level=0):
        self.bounds = (x0, y0, x1, y1)
        self.level = level
        self.children = []
        self.skeleton = None

def build_quadtree(density, x0, y0, x1, y1, level=0, max_level=4, min_density=1):
    patch = density[y0:y1, x0:x1]
    node = QuadtreeNode(x0, y0, x1, y1, level)

    if level == max_level or np.count_nonzero(patch) <= min_density:
        node.skeleton = skeletonize(patch > 0)
        return node

    mx = (x0 + x1) // 2
    my = (y0 + y1) // 2
    node.children = [
        build_quadtree(density, x0, y0, mx, my, level+1, max_level),
        build_quadtree(density, mx, y0, x1, my, level+1, max_level),
        build_quadtree(density, x0, my, mx, y1, level+1, max_level),
        build_quadtree(density, mx, my, x1, y1, level+1, max_level),
    ]
    return node

def render_tile(skeleton_mask, out_path, tile_size=256):
    img = Image.fromarray((skeleton_mask * 255).astype(np.uint8))
    img = img.resize((tile_size, tile_size), Image.NEAREST)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)

def generate_tiles(quadtree_node, tile_size=256, out_dir="tiles"):
    if quadtree_node.children:
        for child in quadtree_node.children:
            generate_tiles(child, tile_size, out_dir)
    elif quadtree_node.skeleton is not None:
        z = quadtree_node.level
        x = quadtree_node.bounds[0] // tile_size
        y = quadtree_node.bounds[1] // tile_size
        path = os.path.join(out_dir, str(z), str(x), f"{y}.png")
        render_tile(quadtree_node.skeleton, path, tile_size)

### ----------------------------
### Density Utilities
### ----------------------------

def draw_line_density(lines, base_max_dim=512):
    all_points = np.array([pt for line in lines for pt in line])
    x = all_points[:, 0]
    y = all_points[:, 1]

    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()

    width_range = x_max - x_min
    height_range = y_max - y_min
    max_range = max(width_range, height_range)

    # Force square canvas
    width = height = base_max_dim
    density = np.zeros((height, width), dtype=np.float32)

    # Pad coordinates to center layout in square
    def scale_coords(pt):
        sx = (pt[0] - x_min) / max_range * (width - 1)
        sy = (pt[1] - y_min) / max_range * (height - 1)
        return int(sy), int(sx)  # row, col

    for start, end in lines:
        r0, c0 = scale_coords(start)
        r1, c1 = scale_coords(end)
        rr, cc = draw_line(r0, c0, r1, c1)
        rr = np.clip(rr, 0, height - 1)
        cc = np.clip(cc, 0, width - 1)
        density[rr, cc] += 1

    return density


### ----------------------------
### Entry Point
### ----------------------------

def get_graph_skeleton(layout_file, tile_out_dir="tiles", quadtree_max_level=5):
    layout_coords = parser.parse_layout_file_coords(layout_file)
    lines = parser.line_pairs(layout_coords)

    # Step 1: Compute density map
    density_map = draw_line_density(lines, base_max_dim=2**quadtree_max_level * 256)

    # Step 2: Visualize base skeleton
    binary = density_map > 0
    skeleton = skeletonize(binary)

    plt.imshow(skeleton, cmap='gray', origin='lower')
    plt.title("Coarse Skeleton (Zoom Level 0)")
    plt.axis('off')
    plt.show()

    # Step 3: Build and tile quadtree
    h, w = density_map.shape
    root = build_quadtree(density_map, 0, 0, w, h, max_level=quadtree_max_level)
    generate_tiles(root, tile_size=256, out_dir=tile_out_dir)

    print(f"✅ Tiles written to: {tile_out_dir}/")

