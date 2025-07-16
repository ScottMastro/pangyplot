import BubbleGun.Node as BubbleGunNode
import BubbleGun.Graph as BubbleGunGraph
import BubbleGun.find_bubbles as BubbleGunFindBubbles
import BubbleGun.connect_bubbles as BubbleGunConnectBubbles
import BubbleGun.find_parents as BubbleGunFindParents
import preprocess2.compact_graph as compacter

from preprocess2.BubbleData import BubbleData
from preprocess2.BubbleIndex import BubbleIndex

import preprocess2.bubble_gun_utils as utils
from collections import defaultdict
import time

def to_bubblegun_obj(segments, links):

    nodes = dict()

    for sid in segments:
        segment = segments[sid]
        sid = str(sid)
        node = BubbleGunNode.Node(sid)
        node.seq = segment["seq"]
        node.seq_len = segment["length"]
        info = {
            "ref": segment["ref"],
            "gc_count": segment["gc_count"],
            "n_count": segment["n_count"],
            "compacted": []
        }
        node.optional_info = info
        nodes[sid] = node

    for from_id, to_id in links:
        link = links[(from_id, to_id)]
        from_id = str(from_id)
        to_id = str(to_id)

        from_strand = link["from_strand"]
        to_strand = link["to_strand"]

        overlap = 0
        
        from_start = (from_strand == "-")
        to_end = (to_strand == "-")

        if not from_start and not to_end:  #  + +
            nodes[from_id].end.add((to_id, 0, overlap))
            nodes[to_id].start.add((from_id, 1, overlap))
        elif not from_start and to_end:  # + -
            nodes[from_id].end.add((to_id, 1, overlap))
            nodes[to_id].end.add((from_id, 1, overlap))
        elif from_start and not to_end:  # - +
            nodes[from_id].start.add((to_id, 0, overlap))
            nodes[to_id].start.add((from_id, 0, overlap))
        elif from_start and to_end:  # - -
            nodes[from_id].start.add((to_id, 1, overlap))
            nodes[to_id].end.add((from_id, 0, overlap))

    return nodes

def find_siblings(bubbles):
    sib_dict = defaultdict(set)
    
    for bubble in bubbles:
        for sid in bubble.get_sibling_segments():
            sib_dict[sid].add(bubble)

    for bubble in bubbles:
        for sid in bubble.get_sibling_segments():
            for sibling in sib_dict[sid]:
                if sibling.id != bubble.id:
                    bubble.add_sibling(sibling.id, sid)

def find_parent_children(bubbles):
    bubble_dict = {bubble.id: bubble for bubble in bubbles}

    for bubble in bubbles:
        if bubble.parent:
            bubble_parent = bubble_dict[bubble.parent]
            bubble_parent.add_child(bubble, bubble_dict)

def construct_bubble_index(graph):
    bubbles = []

    for raw_chain in graph.b_chains:
        chain_id = f"c{raw_chain.id}"
        # note: raw_chain.ends not used (yet?)

        if not raw_chain.sorted: 
            raw_chain.sort()

        chain_bubbles = []
        for raw_bubble in raw_chain.sorted:
            bubble = BubbleData(raw_bubble, chain_id)
            chain_bubbles.append(bubble)

        find_siblings(chain_bubbles)
        bubbles.extend(chain_bubbles)

    find_parent_children(bubbles)

    bubble_index = BubbleIndex(bubbles)

    return bubble_index

def shoot(segments, links):
    print("➡️ Finding bubbles.")

    graph = BubbleGunGraph.Graph()

    print("   🔫 Loading BubbleGun...", end="")
    start_time = time.time()
    graph.nodes = to_bubblegun_obj(segments, links)
    end_time = time.time()
    print(f" Done. Took {round(end_time - start_time,1)} seconds.")
    print(f"      {len(graph.nodes)} segments total.")

    print("   🗜️ Compacting graph...")
    before = len(graph.nodes)
    compacter.compact_graph(graph)
    after = len(graph.nodes)
    print(f"      {before - after} segments were compacted.")

    print("   ⛓️  Finding bubbles and chains...", end="")
    start_time = time.time()
    BubbleGunFindBubbles.find_bubbles(graph)
    BubbleGunConnectBubbles.connect_bubbles(graph)
    BubbleGunFindParents.find_parents(graph)
    end_time = time.time()
    print(f" Done. Took {round(end_time - start_time,1)} seconds.")

    bubbleCount = graph.bubble_number()
    print("   🔘 Simple Bubbles: {}, Superbubbles: {}, Insertions: {}".format(bubbleCount[0], bubbleCount[1], bubbleCount[2]))

    print("   🗃️ Constructing bubble index...", end="")
    start_time = time.time()
    bubble_index = construct_bubble_index(graph)
    end_time = time.time()
    print(f" Done. Took {round(end_time - start_time,1)} seconds.")
    
    #print("   Generating plot.")
    #utils.plot_bubbles(bubbles, output_path="bubbles.plot.svg")

    return bubble_index