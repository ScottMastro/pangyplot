import db.neo4j.neo4j_db as db
import random
from pympler.asizeof import asizeof
import parser.parse_gfa as parse_gfa
import preprocess.bubble.bubble_gun as bubble_gun

from parser.parse_layout import parse_layout
from preprocess.bubble.construct_bubble_index import construct_bubble_index
from utils.export_gfa import export_subgraph_to_gfa

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

    from preprocess.gfa.data_structures.GFAIndex import GFAIndex
    from db.objects.StepIndex import StepIndex
    from preprocess.bubble.BubbleIndex import BubbleIndex

    gfa_index = GFAIndex(CHR_PATH)
    print(f"GFAIndex size:      {asizeof(gfa_index) / 1024**2:.2f} MB")
    step_index = StepIndex(CHR_PATH)
    print(f"step_index size:      {asizeof(step_index) / 1024**2:.2f} MB")
    bubble_index = BubbleIndex(CHR_PATH)
    print(f"bubble_index size:      {asizeof(bubble_index) / 1024**2:.2f} MB")

    ##################################################


    def query_index(start_step, end_step):
        
        bubble_results = bubble_index.get_top_level_bubbles(start_step, end_step, as_chains=False)
        bubble_graph = bubble_index.to_bubble_graph(bubble_results)

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
   
    CHRY_LENGTH=26669912
    CHRY_START=220904
    
    while True:

        START = random.randint(CHRY_START, CHRY_LENGTH)
        END = START + 10000

        #START=18671929 ; END=18681929 #70895+,70800-,70896+
        #START=24891714 ; END=24901714 # WAY TOO MANY NODES
        #START=20198182 ; END=20208182 # large but seems to work

        START_STEP, END_STEP = step_index.query(START, END, debug=False)

        sids = query_index(START_STEP, END_STEP)

        #for bubble in bubbles:
        #    print(bubble_index[bubble.id])

        #print(bubble_index["b53850"])
        #print(bubble_index["b53851"])
        #print(bubble_index["b53852"])
        #print(bubble_index["b53853"])
        #print(bubble_index["b53854"])


        x = sids["bubbles"]
        x.update(sids["segments"])

        #all_ids = list(j-x)
        #inv_all_ids = list(x-j)
        
        if len(xids["segments"]) > 1:
            center = random.choice(list(xids["segments"]))
            export_subgraph_to_gfa(gfa_index, center, "debug_subgraph.gfa", search_distance=1000)

        '''
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
       
        '''
        print("##################################################")
        print(f"FROM INDEX:")
        print("SUBGRAPHS:", sorted(list(xids["subgraphs"])))
        print("-")
        print("SEGMENTS:", sorted(list(xids["segments"])))
        print("-")
        print("BUBBLES:", sorted(list(xids["bubbles"])))
        
        '''
        print("##################################################")
        print("Comparing DB and Index node IDs...")
        print("DIFF:", inv_all_ids)
        '''


        input("Press Enter to continue...")

if __name__ == "__main__":
    main()

