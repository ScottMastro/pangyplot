import db.neo4j_db as db
import random
from pympler.asizeof import asizeof
import preprocess2.gfa.parse_gfa as parse_gfa
from parser.parse_layout import parse_layout
from db.query.query_top_level import get_top_level_data
import db.query.query_node as qnode
import preprocess2.bubble.bubble_gun as bubble_gun
from preprocess2.gfa.parse_gfa import parse_gfa
from preprocess2.bubble.construct_bubble_index import construct_bubble_index

def main():

    db.db_init("chrY")
    db.initiate_collection(1)

    ##################################################

    LAY="static/data/chrY/chrY.sorted.norm.layout.tsv.gz"
    GFA="static/data/chrY/chrY.sorted.norm.gfa.gz"
    REF_PATH="GRCh38#chrY"
    CHR_PATH="datastore/hprc.clip/chrY"

    #skeleton.get_graph_skeleton(LAY)

    recreate_index=False

    if recreate_index:

        layout_coords = parse_layout(LAY)
        segment_dict, link_dict  = parse_gfa(GFA, REF_PATH, layout_coords, CHR_PATH)
        bubble_gun_graph = bubble_gun.shoot(segment_dict, link_dict)
        bubble_index = construct_bubble_index(bubble_gun_graph, CHR_PATH)

    from preprocess2.gfa.data_structures.GFAIndex import GFAIndex
    from preprocess2.StepIndex import StepIndex
    from preprocess2.bubble.BubbleIndex import BubbleIndex

    gfa_index = GFAIndex(CHR_PATH)
    print(f"GFAIndex size:      {asizeof(gfa_index) / 1024**2:.2f} MB")
    step_index = StepIndex(CHR_PATH)
    print(f"step_index size:      {asizeof(step_index) / 1024**2:.2f} MB")
    bubble_index = BubbleIndex(CHR_PATH)
    print(f"bubble_index size:      {asizeof(bubble_index) / 1024**2:.2f} MB")

    ##################################################

    CHRY_LENGTH=26669912
    CHRY_START=220904
    
    def query_neo4j(start, end):
        db_nodes, db_links = get_top_level_data("GRCh38", "chrY", start, end)

        node_ids = {
            "segments": {int(node["id"]) for node in db_nodes if node and node["type"] == "segment"},
            "bubbles": set()
        }

        db_bubbles = [node for node in db_nodes if node and node["type"] == "bubble"]
        db_chains = [node for node in db_nodes if node and node["type"] == "chain"]

        descendant_ids = set()

        for bubble in db_bubbles:
            descendant_ids.update(qnode.get_bubble_descendants(bubble["uuid"]))

        for chain in db_chains:
            descendant_ids.update(qnode.get_chain_descendants(chain["uuid"]))

        node_ids["bubbles"].update(int(nid) for nid in descendant_ids)

        return node_ids

    #########################################################################################################

    def query_index(start_step, end_step):
        
        bubble_results = bubble_index.get_top_level_bubbles(start_step, end_step, as_chains=False)
        bubble_intervals = bubble_index.get_merged_intervals(bubble_results, start_step, end_step)

        subgraphs = []
        for i in range(len(bubble_intervals) - 1):
            gap_start = bubble_intervals[i][1]
            gap_end = bubble_intervals[i+1][0]
            #print("subgraph considered:", gap_start, "->", gap_end)
            subgraphs.append(gfa_index.bfs_subgraph(gap_start, gap_end, step_index))
        
        node_ids = dict()

        node_ids["subgraphs"] = set()
        for subgraph in subgraphs: node_ids["subgraphs"].update(subgraph)

        node_ids["segments"] = bubble_index.get_sibling_segments(bubble_results)
        node_ids["segments"].update(node_ids["subgraphs"])

        node_ids["bubbles"] = set()
        for bubble in bubble_results:
            node_ids["bubbles"].update(bubble_index.get_descendant_ids(bubble))
        return node_ids

    #########################################################################################################

    while True:

        START = random.randint(CHRY_START, CHRY_LENGTH)
        END = START + 10000

        #START=18671929 ; END=18681929 #70895+,70800-,70896+
        #START=24891714 ; END=24901714 # WAY TOO MANY NODES
        #START=20198182 ; END=20208182 # large but seems to work

        START_STEP, END_STEP = step_index.query(START, END, debug=False)

        jids = query_neo4j(START, END)
        xids = query_index(START_STEP, END_STEP)

        #for bubble in bubbles:
        #    print(bubble_index[bubble.id])

        #print(bubble_index["b53850"])
        #print(bubble_index["b53851"])
        #print(bubble_index["b53852"])
        #print(bubble_index["b53853"])
        #print(bubble_index["b53854"])

        j = jids["bubbles"]
        j.update(jids["segments"])
        
        x = xids["bubbles"]
        x.update(xids["segments"])
        
        all_ids = list(j-x)
        inv_all_ids = list(x-j)

        if len(inv_all_ids) > 100:
            print(x)
            print(gfa_index.filter_path(x, step_index))
            print(inv_all_ids)

            gfa_index.export_subgraph_to_gfa(random.choice(inv_all_ids), "debug_subgraph.gfa", max_steps=1000)

        if len(inv_all_ids) <= 100:
            print(".", end="", flush=True)
            continue

        step_index.query(START, END, debug=True)

        print("""MATCH (start:Segment {id: "XXXXXX"})
              MATCH (start)-[:LINKS_TO*1..5]-(neighbor:Segment)
              RETURN DISTINCT neighbor""")

        print("##################################################")
        print(f"Querying top-level bubbles for range {START}-{END}...")
        
        print("##################################################")
        print(f"FROM NEO4J:")
        print("SEGMENTS:", sorted(list(jids["segments"])))
        print("-")
        print("BUBBLES:", sorted(list(jids["bubbles"])))
       
        print("##################################################")
        print(f"FROM INDEX:")
        print("SUBGRAPHS:", sorted(list(xids["subgraphs"])))
        print("-")
        print("SEGMENTS:", sorted(list(xids["segments"])))
        print("-")
        print("BUBBLES:", sorted(list(xids["bubbles"])))

        print("##################################################")
        print("Comparing DB and Index node IDs...")
        print("DIFF:", inv_all_ids)

        input("Press Enter to continue...")

if __name__ == "__main__":
    main()

