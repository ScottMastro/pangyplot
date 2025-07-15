from flask import Flask
import db.neo4j_db as db

import preprocess2.bubble_gun as bubble_gun
import preprocess2.pickle as pkl
import preprocess2.position_index as posidx
import preprocess2.skeletonize as skeleton
import preprocess2.parse_gfa as parse_gfa
import preprocess2.parse_layout as parse_layout
from db.query.query_top_level import get_top_level_data
import db.query.query_node as qnode

app = Flask(__name__)

def main():

    db.db_init("chrY")
    db.initiate_collection(1)

    ##################################################

    LAY="static/data/chrY.sorted.norm.layout.tsv"
    GFA="static/data/chrY.sorted.norm.gfa"
    REF_PATH="GRCh38#chrY"

    #skeleton.get_graph_skeleton(LAY)

    recreate_index=False

    if recreate_index:
        layout_coords = parse_layout.parse_layout(LAY)
        segments, links, sample_idx = parse_gfa.parse_graph(GFA, REF_PATH, layout_coords)
        gfa_index = {"segments": segments, "links": links, "sample_idx": sample_idx}
        pkl.dump_pickle(gfa_index, "gfa_index.pkl")

    if recreate_index:
        bubble_index = bubble_gun.shoot(segments, links)
        pkl.dump_pickle(bubble_index, "bubble_index.pkl")

    if recreate_index:
        index = posidx.build_path_position_index(GFA, REF_PATH)
        pkl.dump_pickle(index, "position_index.pkl")


    position_index = pkl.load_pickle("position_index.pkl")
    bubble_index = pkl.load_pickle("bubble_index.pkl")
    gfa_index = pkl.load_pickle("gfa_index.pkl")

    ##################################################

    START=22402050
    END=22418970

    print(f"Querying top-level bubbles for range {START}-{END}...")
    #query.get_top_level_data(GFA, START, END)

    db_nodes, db_links = get_top_level_data("GRCh38", "chrY", START, END)
    db_bubbles = [node for node in db_nodes if node and node["type"] == "bubble"]

    db_node_ids = dict()
    db_node_ids["segments"] = {node["id"] for node in db_nodes if node and node["type"] == "segment"}

    db_node_ids["bubbles"] = set()
    for bubble in db_bubbles:
        child_segment_ids = qnode.get_bubble_descendants(bubble["uuid"])
        db_node_ids["bubbles"].update(child_segment_ids)

    print("SEGMENTS:", sorted(list(db_node_ids["segments"])))
    print("-")
    print("BUBBLES:", sorted(list(db_node_ids["bubbles"])))

    print("##################################################")
    

    start_node, end_node = position_index.query(START, END, debug=True)
    result = bubble_index.get_top_level_bubbles(start_node, end_node, as_chains=False)
    
    idx_node_ids = set()
    for bubble in result:
        idx_node_ids.update(bubble_index.get_descendant_ids(bubble.id))

    idx_node_ids = {str(nid) for nid in idx_node_ids}
    print(sorted(list(idx_node_ids)))

    print("##################################################")
    print(sorted(list(db_node_ids["bubbles"] - idx_node_ids)))

if __name__ == "__main__":
    main()

