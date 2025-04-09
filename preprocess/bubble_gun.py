import BubbleGun.Node as BubbleGunNode
import BubbleGun.Graph as BubbleGunGraph
import BubbleGun.find_bubbles as BubbleGunFindBubbles
import BubbleGun.connect_bubbles as BubbleGunConnectBubbles
import BubbleGun.find_parents as BubbleGunFindParents


import preprocess.bubble_gun_utils as utils

import db.modify.drop_data as drop
import db.modify.preprocess_modifications as modify
import db.query.query_preprocess as query

import preprocess.compact_graph as compacter

from db.insert.insert_aggregate import insert_bubbles_and_chains
from db.insert.insert_subgraph import insert_subgraphs

from collections import defaultdict

import time

def read_from_db():
    nodes = dict()
    linkDict = {}

    # ==== SEGMENTS ====
    print("   📦 Summarizing segments from database...")
    segments = query.all_segment_summary()

    for s in segments:
        nid, nlen, nref = s
        nid = str(nid)
        nodes[nid] = BubbleGunNode.Node(nid)
        nodes[nid].seq_len = nlen
        nodes[nid].optional_info = {"ref": nref}

    # ==== LINKS ====
    print("   🚚 Summarizing links from database...")
    links = query.all_link_summary()

    for from_strand, first_node, to_strand, second_node in links:
        first_node = str(first_node)
        second_node = str(second_node)
        overlap = 0

        if first_node not in linkDict:
            linkDict[first_node] = set()
        linkDict[first_node].add(second_node)

        from_start = (from_strand == "-")
        to_end = (to_strand == "-")

        if not from_start and not to_end:  #  + +
            nodes[first_node].end.add((second_node, 0, overlap))
            nodes[second_node].start.add((first_node, 1, overlap))
        elif not from_start and to_end:  # + -
            nodes[first_node].end.add((second_node, 1, overlap))
            nodes[second_node].end.add((first_node, 1, overlap))
        elif from_start and not to_end:  # - +
            nodes[first_node].start.add((second_node, 0, overlap))
            nodes[second_node].start.add((first_node, 0, overlap))
        elif from_start and to_end:  # - -
            nodes[first_node].start.add((second_node, 1, overlap))
            nodes[second_node].end.add((first_node, 0, overlap))

    return nodes


def insert_all(graph, merged_map):
    child_bubbles = defaultdict(list)
    bubble_dict = {}

    for chain in graph.b_chains:
        for bubble in chain.bubbles:
            bubble_dict[bubble.id] = bubble
            if bubble.parent_sb:
                child_bubbles[bubble.parent_sb].append(bubble)

    bubble_metadata = utils.assign_bubble_depths(bubble_dict, child_bubbles)

    chains, bubbles = [], []

    for chain in graph.b_chains:
        for bubble in chain.bubbles:
            subtype = "simple"
            if bubble.is_insertion():
                subtype = "insertion"

            inside_ids = {seg.id for seg in bubble.inside}
            compacted_ids = set()
            for sid in inside_ids:
                if sid in merged_map:
                    compacted_ids.update(merged_map[sid])
            inside_ids.update(compacted_ids)

            if bubble.is_super():
                subtype = "super"
                for child in child_bubbles.get(bubble.id, []):
                    inside_ids -= {seg.id for seg in child.inside}
 
            meta = bubble_metadata[bubble.id]
            bubbles.append({
                "id": bubble.id,
                "subtype": subtype,
                "ends": [bubble.source.id, bubble.sink.id],
                "sb": None if not bubble.parent_sb else bubble.parent_sb,
                "pc": None if not bubble.parent_chain else bubble.parent_chain,
                "nesting_level": meta["nesting_level"],
                "depth": meta["depth"],
                "inside": sorted(inside_ids),
            })

        if len(chain.bubbles) < 2:
            continue

        chains.append({
            "id": chain.id,
            "subtype": "chain",
            "ends": [chain.ends[1], chain.ends[0]],
            "sb": None if not chain.parent_sb else chain.parent_sb,
            "pc": None if not chain.parent_chain else chain.parent_chain,
            "nesting_level": bubble_metadata.get(chain.parent_sb, {}).get("nesting_level", 0),
            "depth": max(bubble_metadata[b.id]["depth"] for b in chain.bubbles),
            "inside": [bubble.id for bubble in chain.bubbles]
        })

    insert_bubbles_and_chains(bubbles, chains)


def shoot(altgraphs):

    graph = BubbleGunGraph.Graph()
    graph.nodes = read_from_db()

    print("   🗜️ Compacting graph...")
    before = len(graph.nodes)
    merged_map = compacter.compact_graph(graph)
    modify.create_compact_links(merged_map)
    after = len(graph.nodes)
    print(f"      Segments compacted; Total: {before} ➜ {after}.")

    print("   ⛓️  Finding bubble chains...")
    start_time = time.time()
    BubbleGunFindBubbles.find_bubbles(graph)
    end_time = time.time()
    print(f"      Took {round(end_time - start_time,1)} seconds.")

    print("   🔗 Connecting bubbles...")
    start_time = time.time()
    BubbleGunConnectBubbles.connect_bubbles(graph)
    end_time = time.time()
    print(f"      Took {round(end_time - start_time,1)} seconds.")

    print("   🏗 Building bubble hierarchy...")
    start_time = time.time()
    BubbleGunFindParents.find_parents(graph)
    end_time = time.time()
    print(f"      Took {round(end_time - start_time,1)} seconds.")


    normalize_bubble_direction(graph)


    bubbleCount = graph.bubble_number()
    print("   🔘 Simple Bubbles: {}, Superbubbles: {}, Insertions: {}".format(bubbleCount[0], bubbleCount[1], bubbleCount[2]))

    print("   🗃️ Adding to database...")
    start_time = time.time()
    insert_all(graph, merged_map)
    end_time = time.time()
    print(f"      Took {round(end_time - start_time,1)} seconds.")

    print("   🚩 Annotating deletions...")
    modify.annotate_deletions()

    if altgraphs:
        print("   🌿 Building alternative path branches...")
        #drop.drop_anchors()
        #drop.drop_subgraphs()
        subgraphs = utils.create_alt_subgraphs(graph)
        insert_subgraphs(subgraphs)

        print("   ⚓ Anchoring alt branches...")
        modify.anchor_alternative_branches()
        drop.drop_subgraphs()
    
    print("   Done.")