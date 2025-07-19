import os
from preprocess2.StepIndex import StepIndex
import preprocess2.bubble.bubble_index_utils as utils
import matplotlib.pyplot as plt 
import preprocess2.db.bubble_db as db

def construct_bubble_index(bubble_gun_graph, chr_dir, plot=False):
    step_index = StepIndex(chr_dir)
    step_dict = step_index.get_segment_to_steps_dict()

    bubbles = []

    for raw_chain in bubble_gun_graph.b_chains:
        chain_id = f"c{raw_chain.id}"
        # note: raw_chain.ends not used (do we need to?)

        if not raw_chain.sorted: 
            raw_chain.sort()

        chain_bubbles = []
        for chain_step, raw_bubble in enumerate(raw_chain.sorted):
            bubble = utils.create_bubble_object(raw_bubble, chain_id, chain_step, step_dict)

            chain_bubbles.append(bubble)

        utils.find_siblings(chain_bubbles)
        bubbles.extend(chain_bubbles)

    utils.find_parent_children(bubbles)

    conn = db.create_bubble_tables(chr_dir)
    db.insert_bubbles(conn, bubbles)

    if plot:
        plot_path = os.path.join(chr_dir, "bubbles.plot.svg")
        plot_bubbles(bubbles, output_path=plot_path)

    return bubbles

def plot_bubbles(bubbles, output_path, min_height=None):
    bubble_dict = {bubble.id: bubble for bubble in bubbles}

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
