import argparse
from flask import Flask
import db.neo4j_db as db
import preprocess.bubble_gun as bubble_gun
import db.insert.insert_metadata as metadata
import preprocess.bubble_gun_utils as bubble_utils

import pickle

app = Flask(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description="Debug tools for PangyPlot development.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: pickle
    parser_bubbles = subparsers.add_parser("pickle", help="Get a pickled version of a graph.")
    parser_bubbles.add_argument("--db", type=str, required=True, help="Database ID to extract.")
    parser_bubbles.add_argument("--collection", type=int, required=True, help="Collection ID to extract.")
    parser_bubbles.add_argument("--out", type=str, default="bubble_graph.pkl", help="Output path for pickle file (default: bubble_graph.pkl)")

    parser_bubbles = subparsers.add_parser("analysis", help="Run analysis on a pickled graph.")
    parser_bubbles.add_argument("--graph", type=str, required=True, default="bubble_graph.pkl", help="Pickled graph.")


    return parser.parse_args()

def main():
    args = parse_args()

    if args.command == "pickle":

        db.db_init(args.db)

        db.initiate_collection(args.collection)
        graph = bubble_gun.shoot(add_to_db=False)

        with open(args.out, "wb") as f:
            pickle.dump(graph, f)
        print(f"💾 Graph written to {args.out}")

    if args.command == "analysis":

        with open(args.graph, "rb") as f:
            graph = pickle.load(f)
        print(f"📂 Graph loaded from {args.graph}")
    
        analysis(graph)

import matplotlib.pyplot as plt

def analysis(graph):
    print("   🌿 Building alternative path branches...")
    subgraphs = bubble_utils.create_alt_subgraphs(graph)
    print(f"   📊 Found {len(subgraphs)} alternative subgraphs.")

    # Gather statistics
    node_counts = [len(sg["graph"]) for sg in subgraphs]
    anchor_counts = [len(sg["anchor"]) for sg in subgraphs]

    print(f"   🧮 Node stats - min: {min(node_counts)}, max: {max(node_counts)}, mean: {sum(node_counts)/len(node_counts):.2f}")
    print(f"   🧮 Anchor stats - min: {min(anchor_counts)}, max: {max(anchor_counts)}, mean: {sum(anchor_counts)/len(anchor_counts):.2f}")

    # Step 2: Count bubbles
    simple, super_, insertion = graph.bubble_number()

    # Step 3: Count chains
    total_chains = len(graph.b_chains)

    # Step 4: Compute nodes with 'ref' info
    def count_ref(nodeset):
        return sum(1 for n in nodeset if graph.nodes[n].optional_info.get("ref") is not None)

    # All nodes in chains
    nodes_in_chains = graph.nodes_in_chains()
    nodes_in_simple = set()
    nodes_in_super = set()

    for b in graph.bubbles.values():
        node_ids = set(b.list_bubble())
        if b.is_simple():
            nodes_in_simple |= node_ids
        elif b.is_super():
            nodes_in_super |= node_ids

    # Total nodes with "ref" in the whole graph
    all_ref = count_ref(graph.nodes.keys())
    ref_in_chains = count_ref(nodes_in_chains)
    ref_in_simple = count_ref(nodes_in_simple)
    ref_in_super = count_ref(nodes_in_super)

    stats = {
        "counts": {
            "simple_bubbles": simple,
            "superbubbles": super_,
            "insertion_bubbles": insertion,
            "chains": total_chains
        },
        "ref_distribution": {
            "total_ref_nodes": all_ref,
            "ref_in_chains": ref_in_chains,
            "ref_in_simple_bubbles": ref_in_simple,
            "ref_in_superbubbles": ref_in_super
        },
        "proportions": {
            "ref_in_chains_%": 100 * ref_in_chains / len(nodes_in_chains) if nodes_in_chains else 0,
            "ref_in_simple_bubbles_%": 100 * ref_in_simple / len(nodes_in_simple) if nodes_in_simple else 0,
            "ref_in_superbubbles_%": 100 * ref_in_super / len(nodes_in_super) if nodes_in_super else 0,
        }
    }

    print("Category\tCount")
    print(f"Simple_Bubbles\t{stats['counts']['simple_bubbles']}")
    print(f"Superbubbles\t{stats['counts']['superbubbles']}")
    print(f"Insertion_Bubbles\t{stats['counts']['insertion_bubbles']}")
    print(f"Chains\t{stats['counts']['chains']}\n")

    print("Category\tRef_Nodes")
    print(f"Total_Ref_Nodes\t{stats['ref_distribution']['total_ref_nodes']}")
    print(f"Ref_in_Chains\t{stats['ref_distribution']['ref_in_chains']}")
    print(f"Ref_in_Simple_Bubbles\t{stats['ref_distribution']['ref_in_simple_bubbles']}")
    print(f"Ref_in_Superbubbles\t{stats['ref_distribution']['ref_in_superbubbles']}\n")

    print("Category\tPercentage")
    print(f"Ref_in_Chains(%)\t{stats['proportions']['ref_in_chains_%']:.2f}")
    print(f"Ref_in_Simple_Bubbles(%)\t{stats['proportions']['ref_in_simple_bubbles_%']:.2f}")
    print(f"Ref_in_Superbubbles(%)\t{stats['proportions']['ref_in_superbubbles_%']:.2f}")

if __name__ == "__main__":
    main()

