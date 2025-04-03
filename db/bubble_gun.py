from BubbleGun.Graph import Graph
from BubbleGun.Node import Node
from BubbleGun.find_bubbles import find_bubbles
from BubbleGun.connect_bubbles import connect_bubbles
from BubbleGun.find_parents import find_parents

import db.modify.drop_data as drop
from db.query.query_all import query_all_segments, query_all_links
import db.modify.compact_graph as compacter 
import db.modify.graph_modify as modify

from db.insert.insert_bubble import insert_bubbles, add_bubble_properties
from db.insert.insert_chain import insert_chains, add_chain_properties
from db.insert.insert_subgraph import insert_subgraph

from collections import deque
import time

def read_from_db():
    nodes = dict()

    print("Getting segments...")
    segments = query_all_segments()

    for s in segments:
        nid, nlen, nref = s
        nid = str(nid)
        nodes[nid] = Node(nid)
        nodes[nid].seq_len = nlen
        nodes[nid].optional_info = {"ref": nref}
        #nodes[nid].seq = ...

    print("Getting links...")
    edges = query_all_links()

    edgeDict = {}
    for e in edges:
        from_strand, first_node, to_strand, second_node = e
        first_node=str(first_node)
        second_node=str(second_node)
        overlap = 0

        if first_node not in edgeDict:
            edgeDict[first_node] = set()

        if second_node in edgeDict[first_node]:
            print("DUPLICATE", first_node, second_node)

        edgeDict[first_node].add(second_node)

        if from_strand == "-":
            from_start = True
        else:
            from_start = False
        if to_strand == "-":
            to_end = True
        else:
            to_end = False

        if from_start and to_end:  # from start to end L x - y -
            if (second_node, 1, overlap) not in nodes[first_node].start:
                nodes[first_node].start.append((second_node, 1, overlap))
            if (first_node, 0, overlap) not in nodes[second_node].end:
                nodes[second_node].end.append((first_node, 0, overlap))
        elif from_start and not to_end:  # from start to start L x - y +
            if (second_node, 0, overlap) not in nodes[first_node].start:
                nodes[first_node].start.append((second_node, 0, overlap))
            if (first_node, 0, overlap) not in nodes[second_node].start:
                nodes[second_node].start.append((first_node, 0, overlap))
        elif not from_start and not to_end:  # from end to start L x + y +
            if (second_node, 0, overlap) not in nodes[first_node].end:
                nodes[first_node].end.append((second_node, 0, overlap))
            if (first_node, 1, overlap) not in nodes[second_node].start:
                nodes[second_node].start.append((first_node, 1, overlap))
        elif not from_start and to_end:  # from end to end L x + y -
            if (second_node, 1, overlap) not in nodes[first_node].end:
                nodes[first_node].end.append((second_node, 1, overlap))
            if (first_node, 1, overlap) not in nodes[second_node].end:
                nodes[second_node].end.append((first_node, 1, overlap))

    return nodes



def insert_all(graph):
    chains,bubbles = [], []

    for chain in graph.b_chains:
        chains.append({
                "id": chain.id, 
                "ends": [chain.ends[1], chain.ends[0]],
                "sb": None if not chain.parent_sb else chain.parent_sb,
                "pc": None if not chain.parent_chain else chain.parent_chain,
                "bubbles":[bubble.id for bubble in chain.bubbles]
                })
        
        for bubble in chain.bubbles:
            type = "simple" 
            if bubble.is_super():
                type = "super"
            elif bubble.is_insertion():
                type = "insertion"

            bubbles.append({
                "id": bubble.id,
                "type": type,
                "ends": [bubble.sink.id, bubble.source.id],
                "chain_id": None if not bubble.chain_id else bubble.chain_id,
                "sb": None if not bubble.parent_sb else bubble.parent_sb,
                "pc": None if not bubble.parent_chain else bubble.parent_chain,
                "inside":[segment.id for segment in bubble.inside]
                })
            
    insert_bubbles(bubbles)
    insert_chains(chains)
    add_bubble_properties()
    add_chain_properties()


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


def shoot(compact, altgraphs):

    print("Fetching graph...")
    graph = Graph()
    graph.nodes = read_from_db()

    if compact:
        print("Compacting graph...")
        before = len(graph.nodes)
        compacter.compact_graph(graph)
        after = len(graph.nodes)
        print(f"{after}/{before} segments retained.")
    

    print("Finding bubble chains...")
    start_time = time.time()
    find_bubbles(graph)
    end_time = time.time()
    print(f"Bubble chains found in {end_time - start_time} seconds.")

    print("Connecting bubbles...")
    start_time = time.time()
    connect_bubbles(graph)
    end_time = time.time()
    print(f"Bubbles connected in {end_time - start_time} seconds.")

    print("Building hierarchy...")
    start_time = time.time()
    find_parents(graph)
    end_time = time.time()
    print(f"Hierarchy built in {end_time - start_time} seconds.")

    b_numbers = graph.bubble_number()
    print("The number of Simple Bubbles is {}\n"
        "The number of Superbubbles is {}\n"
        "The number of insertions is {}".format(b_numbers[0], b_numbers[1], b_numbers[2]))

    print("Inserting all data...")
    start_time = time.time()
    insert_all(graph)
    end_time = time.time()
    print(f"Data inserted in {end_time - start_time} seconds.")

    modify.annotate_deletions()
    modify.connect_bubble_ends_to_chain()
    modify.add_chain_subtype()

    if altgraphs:
        print("Building alt branches...")

        #drop.drop_anchors()
        #drop.drop_subgraphs()

        print("Finding alt branches...")
        create_alt_subgraphs(graph)
        
        print("Anchoring alt branches...")
        modify.anchor_alternative_branches()
        drop.drop_subgraphs()