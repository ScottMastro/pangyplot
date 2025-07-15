import matplotlib.pyplot as plt
from collections import defaultdict

def find_siblings(bubbles):
    siblings = defaultdict(set)
    
    for bubble in bubbles:
        ends = bubble['ends']
        for end in ends:
            siblings[end].add(bubble["id"])

    for bubble in bubbles:
        bubble["siblings"] = []
        for end in bubble['ends']:
            for sibling in siblings[end]:
                if sibling != bubble["id"]:
                     #(sib_id,segment_id)
                    bubble["siblings"].append((sibling, end))

def find_children(bubble_dict):
    for bid in bubble_dict:
        bubble_dict[bid]["children"] = []
    for bid in bubble_dict:
        bubble = bubble_dict[bid]    
        if bubble["parent"]:
            parent = bubble_dict[bubble["parent"]]
            parent["children"].append(bubble["id"])

def remove_nested_segments(bubble_dict):
    max_height = max(bubble["height"] for bubble in bubble_dict.values())

    # Loop from max height down to 0
    for h in range(max_height, -1, -1):
        for bid, bubble in bubble_dict.items():
            if bubble["height"] != h:
                continue

            original_nids = set(bubble["inside"])
            nids = set(original_nids)

            for child_id in bubble.get("children", []):
                child_nids = set(bubble_dict[child_id]["inside"])
                nids -= child_nids

            #removed_count = len(original_nids) - len(nids)
            #if removed_count > 0:
            #    print(f"[INFO] Removed {removed_count} nested node(s) from bubble {bid}")

            bubble["inside"] = sorted(nids)


def assign_bubble_levels(bubble_dict):

    def get_depth(bid):
        bubble = bubble_dict[bid]
        if "depth" in bubble:
            return bubble["depth"]
        
        if not bubble["parent"]:
            return 0
        level = 1 + get_depth(bubble["parent"])
        return level

    def get_height(bid):
        bubble = bubble_dict[bid]
        if "height" in bubble:
            return bubble["height"]

        children = bubble["children"]
        if len(children) < 1:
            return 1
        return 1 + max(get_height(c) for c in children)

    for bid in bubble_dict:
        bubble = bubble_dict[bid]
        bubble["height"] = get_height(bid)
        bubble["depth"] = get_depth(bid)

def compute_bubble_properties(graph, bubble):
    nodes = [graph.nodes[str(nid)] for nid in bubble["inside"]]
    ref_ids = [int(node.id) for node in nodes if node.optional_info.get("ref")]
    lengths = [n.seq_len for n in nodes]
    gc_counts = [n.optional_info.get("gc_count", 0) for n in nodes]
    n_counts = [n.optional_info.get("n_count", 0) for n in nodes]
    
    ref_range = []
    if len(ref_ids) == 1:
        ref_range = ref_ids
    elif len(ref_ids) > 1:
        ref_range = [min(ref_ids), max(ref_ids)]

    properties = {
        "range": ref_range,
        "length": sum(lengths),
        "node_count": len(nodes),
        "gc_count": sum(gc_counts),
        "n_count" : sum(n_counts),
        "ref": len(ref_ids) > 0
    }

    bubble.update(properties)

def plot_bubbles(bubble_dict, output_path, min_height=None):
    plt.figure(figsize=(12, 6))

    for bid, bubble in bubble_dict.items():
        if len(bubble["range"]) < 2: 
            continue
        if min_height is not None and bubble["height"] < min_height:
            continue
        
        x = bubble["range"]
        if len(x) == 1: x = [x] * 2

        y = [bubble["height"]] * 2
        plt.plot(x, y, color="blue", lw=2)

        #midpoint = sum(x) / 2
        #plt.text(midpoint, y_val + 0.05, f"{bid}", color="black", fontsize=6, ha="center")

    plt.xlabel("Reference Node ID")
    plt.ylabel("Height")
    plt.title("Bubbles over Reference Path")
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"[INFO] Plot saved to {output_path}")

