from BubbleGun.Graph import Graph
from BubbleGun.Node import Node
from BubbleGun.compact_graph import merge_start,merge_end
from BubbleGun.find_bubbles import find_bubbles
from BubbleGun.connect_bubbles import connect_bubbles
from BubbleGun.find_parents import find_parents

import db.neo4j_query as neo4jdb 
from db.compact_segment import compact_segment 

from db.insert.insert_bubble import insert_bubbles, add_bubble_properties
from db.insert.insert_chain import insert_chains, add_chain_properties

import time

def read_from_db():
    nodes = dict()

    print("Getting segments...")

    segments = neo4jdb.query_all_segments()
    for s in segments:
        n_id, n_len = s
        n_id = str(n_id)
        nodes[n_id] = Node(n_id)
        nodes[n_id].seq_len = n_len
        #nodes[n_id].optional_info = ...
        #nodes[n_id].seq = ...

    print("Getting links...")

    edges = neo4jdb.query_all_links()

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

def compact_graph(graph):
    list_of_nodes = list(graph.nodes.keys())
    for n in list_of_nodes:
        if n in graph.nodes:
            while True:
                if len(graph.nodes[n].end) == 1: 
                    other = graph.nodes[n].end[0][0]
                    merge = merge_end(graph, n)
                    if merge:
                        compact_segment(n, other)
                    else:
                        break
                else:
                    break

            while True:
                if len(graph.nodes[n].start) == 1:
                    other = graph.nodes[n].start[0][0]
                    merge = merge_start(graph, n)
                    if merge:
                        compact_segment(n, other)
                    else:
                        break
                else:
                    break

def insert_all(graph):
    chains,bubbles = [], []

    for chain in graph.b_chains:
        chains.append({
                "id": chain.id, 
                "ends": chain.ends,
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
                "ends": [bubble.source.id, bubble.sink.id],
                "chain_id": None if not bubble.chain_id else bubble.chain_id,
                "sb": None if not bubble.parent_sb else bubble.parent_sb,
                "pc": None if not bubble.parent_chain else bubble.parent_chain,
                "inside":[segment.id for segment in bubble.inside]
                })
            
    insert_bubbles(bubbles)
    insert_chains(chains)
    add_bubble_properties()
    add_chain_properties()


def shoot():

    print("Fetching graph...")
    graph = Graph()
    graph.nodes = read_from_db()

    print("Compacting graph...")
    before = len(graph.nodes)
    compact_graph(graph)
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