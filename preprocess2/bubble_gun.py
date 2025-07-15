import BubbleGun.Node as BubbleGunNode
import BubbleGun.Graph as BubbleGunGraph
import BubbleGun.find_bubbles as BubbleGunFindBubbles
import BubbleGun.connect_bubbles as BubbleGunConnectBubbles
import BubbleGun.find_parents as BubbleGunFindParents

import preprocess2.bubble_gun_utils as utils
import preprocess2.bubble_index as indexer
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
            "n_count": segment["n_count"]
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

def get_bubble_type(bubble):
    if bubble.is_insertion():
        return "insertion"
    elif bubble.is_super():
        return "super"
    else:
        return "simple"

def bubble_from_object(raw_bubble, chain_id):
    bubble = {"id": f"b{raw_bubble.id}"}
    bubble["chain"] = chain_id
    bubble["subtype"] = get_bubble_type(raw_bubble)

    bubble["ends"] = [int(raw_bubble.source.id), int(raw_bubble.sink.id)]
    inside = sorted([int(node.id) for node in raw_bubble.inside])
    bubble["inside"] = inside

    bubble["parent"] = f"b{raw_bubble.parent_sb}" if raw_bubble.parent_sb else None

    return bubble

def postprocess(graph):

    bubble_dict = {}

    for raw_chain in graph.b_chains:
        chain_id = f"c{raw_chain.id}"
        # note: raw_chain.ends not used (yet?)

        if not raw_chain.sorted: 
            raw_chain.sort()

        chain_bubbles = []
        for raw_bubble in raw_chain.sorted:
            bubble = bubble_from_object(raw_bubble, chain_id)
            utils.compute_bubble_properties(graph, bubble)
            chain_bubbles.append(bubble)

        utils.find_siblings(chain_bubbles)
        bubble_dict[bubble["id"]] = bubble

        for bubble in chain_bubbles:
            bubble_dict[bubble["id"]] = bubble
        
    utils.find_children(bubble_dict)
    utils.assign_bubble_levels(bubble_dict)
    utils.remove_nested_segments(bubble_dict)

    return bubble_dict

def shoot(segments, links):
    print("➡️ Finding bubbles.")

    graph = BubbleGunGraph.Graph()

    print("   🔫 Loading BubbleGun...", end="")
    start_time = time.time()
    graph.nodes = to_bubblegun_obj(segments, links)
    end_time = time.time()
    print(f" Done. Took {round(end_time - start_time,1)} seconds.")
    print(f"      Segments Total: {len(graph.nodes)}.")

    print("   ⛓️  Finding bubbles and chains...", end="")
    start_time = time.time()
    BubbleGunFindBubbles.find_bubbles(graph)
    BubbleGunConnectBubbles.connect_bubbles(graph)
    BubbleGunFindParents.find_parents(graph)
    end_time = time.time()
    print(f" Done. Took {round(end_time - start_time,1)} seconds.")

    bubbleCount = graph.bubble_number()
    print("   🔘 Simple Bubbles: {}, Superbubbles: {}, Insertions: {}".format(bubbleCount[0], bubbleCount[1], bubbleCount[2]))

    print("   🗃️ Processing bubbles and chains...", end="")
    start_time = time.time()
    bubble_dict = postprocess(graph)
    bubble_index = indexer.BubbleIndex(graph, bubble_dict)
    end_time = time.time()
    print(f" Done. Took {round(end_time - start_time,1)} seconds.")
    
    #print("   Generating plot.")
    #utils.plot_bubbles(bubble_dict, output_path="bubbles.plot.svg")

    return bubble_index