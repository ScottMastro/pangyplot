from BubbleGun.Graph import Graph
from BubbleGun.Node import Node
from BubbleGun.compact_graph import merge_start,merge_end

import db.neo4j_query as neo4jdb 
from db.compact_segment import compact_segment 

def read_from_db():
    nodes = dict()

    segments = neo4jdb.query_all_segments()
    for s in segments:
        n_id, n_len = s
        nodes[n_id] = Node(n_id)
        nodes[n_id].seq_len = n_len
        #nodes[n_id].optional_info = ...
        #nodes[n_id].seq = ...

    edges = neo4jdb.query_all_links()

    for e in edges:
        from_strand, first_node, to_strand, second_node = e
        overlap = 0

        from_start = from_strand == "-"
        to_end = to_strand == "-"

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

def shoot():
    graph = Graph()
    graph.nodes = read_from_db()

    print(len(graph.nodes))
    compact_graph(graph) 
    print(len(graph.nodes))


