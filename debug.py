import argparse
from flask import Flask
import db.neo4j_db as db
import preprocess.bubble_gun as bubble_gun
import db.insert.insert_metadata as metadata
import preprocess.bubble_gun_utils as utils

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
        bubble_gun.shoot(add_to_db=False)

        with open(args.out, "wb") as f:
            pickle.dump(graph, f)
        print(f"💾 Graph written to {args.out}")

    if args.command == "analysis":

        with open(args.graph, "rb") as f:
            graph = pickle.load(f)
        print(f"📂 Graph loaded from {args.graph}")
    
    analysis(graph)

if __name__ == "__main__":
    main()


def analysis(graph):

    print("   🌿 Building alternative path branches...")
    subgraphs = utils.create_alt_subgraphs(graph)
    