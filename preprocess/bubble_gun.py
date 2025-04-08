from BubbleGun.Graph import Graph
from BubbleGun.Node import Node
from BubbleGun.find_bubbles import find_bubbles
from BubbleGun.connect_bubbles import connect_bubbles
from BubbleGun.find_parents import find_parents

import db.modify.drop_data as drop
import db.modify.preprocess as preprocess
import preprocess.compact_graph as compacter

from db.insert.insert_aggregate import insert_bubbles_and_chains
from db.insert.insert_subgraph import insert_subgraph

from collections import deque, defaultdict

import time

def read_from_db():
    nodes = dict()
    linkDict = {}

    # ==== SEGMENTS ====
    print("   📦 Summarizing segments from database...")
    segments = preprocess.query_segment_summary()

    for s in segments:
        nid, nlen, nref = s
        nid = str(nid)
        nodes[nid] = Node(nid)
        nodes[nid].seq_len = nlen
        nodes[nid].optional_info = {"ref": nref}

    # ==== LINKS ====
    print("   🚚 Summarizing links from database...")
    links = preprocess.query_link_summary()

    for from_strand, first_node, to_strand, second_node in links:
        first_node = str(first_node)
        second_node = str(second_node)
        overlap = 0

        if first_node not in linkDict:
            linkDict[first_node] = set()
        if second_node in linkDict[first_node]:
            print("DUPLICATE", first_node, second_node)
        linkDict[first_node].add(second_node)

        from_start = (from_strand == "-")
        to_end = (to_strand == "-")

        if from_start and to_end:  # from start to end L x - y -
            if (second_node, 1, overlap) not in nodes[first_node].start:
                nodes[first_node].start.add((second_node, 1, overlap))
            if (first_node, 0, overlap) not in nodes[second_node].end:
                nodes[second_node].end.add((first_node, 0, overlap))
        elif from_start and not to_end:  # from start to start L x - y +
            if (second_node, 0, overlap) not in nodes[first_node].start:
                nodes[first_node].start.add((second_node, 0, overlap))
            if (first_node, 0, overlap) not in nodes[second_node].start:
                nodes[second_node].start.add((first_node, 0, overlap))
        elif not from_start and not to_end:  # from end to start L x + y +
            if (second_node, 0, overlap) not in nodes[first_node].end:
                nodes[first_node].end.add((second_node, 0, overlap))
            if (first_node, 1, overlap) not in nodes[second_node].start:
                nodes[second_node].start.add((first_node, 1, overlap))
        elif not from_start and to_end:  # from end to end L x + y -
            if (second_node, 1, overlap) not in nodes[first_node].end:
                nodes[first_node].end.add((second_node, 1, overlap))
            if (first_node, 1, overlap) not in nodes[second_node].end:
                nodes[second_node].end.add((first_node, 1, overlap))

    return nodes

def assign_bubble_depths(graph, bubble_dict, child_bubbles):
    nesting_cache = {}
    depth_cache = {}

    def get_nesting_level(bid):
        if bid in nesting_cache:
            return nesting_cache[bid]
        bubble = bubble_dict.get(bid)
        if not bubble or not bubble.parent_sb:
            nesting_cache[bid] = 0
            return 0
        level = 1 + get_nesting_level(bubble.parent_sb)
        nesting_cache[bid] = level
        return level

    def get_depth_below(bid):
        if bid in depth_cache:
            return depth_cache[bid]
        children = child_bubbles.get(bid, [])
        if not children:
            depth = 0
        else:
            depth = 1 + max(get_depth_below(child.id) for child in children)
        depth_cache[bid] = depth
        return depth

    bubble_metadata = {}
    for bid, bubble in bubble_dict.items():
        bubble_metadata[bid] = {
            "nesting_level": get_nesting_level(bid),
            "depth": get_depth_below(bid),
        }

    return bubble_metadata

def insert_all(graph, merged_map):
    child_bubbles = defaultdict(list)
    bubble_dict = {}

    for chain in graph.b_chains:
        for bubble in chain.bubbles:
            bubble_dict[bubble.id] = bubble
            if bubble.parent_sb:
                child_bubbles[bubble.parent_sb].append(bubble)

    bubble_metadata = assign_bubble_depths(graph, bubble_dict, child_bubbles)

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
                "ends": [bubble.sink.id, bubble.source.id],
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


def bfs_find_subgraph(graph, start_node):
    queue = deque([start_node])
    visited = set()
    refset = set()

    while queue:
        current = queue.popleft()

        if current.optional_info["ref"]:
            refset.add(current.id)
            continue

        if current.id in visited:
            continue

        visited.add(current.id)

        for neighbor in current.neighbors():
            if neighbor not in visited:
                queue.append(graph.nodes[neighbor])

    return {"anchor": refset, "graph": visited}


def create_alt_subgraphs(graph):
    nodes = list(graph.nodes.keys())
    visited = set()

    for nid in nodes:
        node = graph.nodes[nid]
        if nid in visited:
            continue
        if node.optional_info["ref"]:
            visited.add(nid)
            continue
        
        subgraph = bfs_find_subgraph(graph, node)
        for v in subgraph["graph"]:
            visited.add(v)

        if len(subgraph["graph"]) > 1:
            input()
            insert_subgraph(subgraph)


def shoot(altgraphs):

    graph = Graph()
    graph.nodes = read_from_db()

    #compact = False
    #if compact:
    print("   🗜️ Compacting graph...")
    before = len(graph.nodes)
    merged_map = compacter.compact_graph(graph)
    preprocess.create_compact_links(merged_map)
    after = len(graph.nodes)
    print(f"      Segments compacted; Total: {before} ➜ {after}.")

    print("   ⛓️  Finding bubble chains...")
    start_time = time.time()
    find_bubbles(graph)
    end_time = time.time()
    print(f"      Took {round(end_time - start_time,1)} seconds.")

    print("   🔗 Connecting bubbles...")
    start_time = time.time()
    connect_bubbles(graph)
    end_time = time.time()
    print(f"      Took {round(end_time - start_time,1)} seconds.")

    print("   🏗 Building bubble hierarchy...")
    start_time = time.time()
    find_parents(graph)
    end_time = time.time()
    print(f"      Took {round(end_time - start_time,1)} seconds.")

    bubbleCount = graph.bubble_number()
    print("   🔘 Simple Bubbles: {}, Superbubbles: {}, Insertions: {}".format(bubbleCount[0], bubbleCount[1], bubbleCount[2]))

    print("   🗃️ Adding to database...")
    start_time = time.time()
    insert_all(graph, merged_map)
    end_time = time.time()
    print(f"      Took {round(end_time - start_time,1)} seconds.")

    print("   🚩 Annotating deletions...")
    preprocess.annotate_deletions()
    print("done")
    input()

    if altgraphs:
        print("Building alt branches...")

        #drop.drop_anchors()
        #drop.drop_subgraphs()

        print("Finding alt branches...")
        create_alt_subgraphs(graph)
        
        print("Anchoring alt branches...")
        preprocess.anchor_alternative_branches()
        drop.drop_subgraphs()