from segment import SimpleSegment,Bubble

def get_nodes(segment, graph, chr=None, start=None, end=None):
    rows = segment.query.all()
    for row in rows:
        node = SimpleSegment(row.id, group=3, description="desc", size=3,
        chrom=row.chrom, pos=row.pos)
        node.add_source_node(row.x1, row.y1)
        node.add_sink_node(row.x2, row.y2)
        graph[row.id] = node

    return graph

def get_edges(link, graph, chr=None, start=None, end=None):
    rows = link.query.all()
    for row in rows:
        fromNode = graph[row.from_id]
        toNode = graph[row.to_id]
        fromNode.add_link_to(toNode)
        toNode.add_link_from(fromNode)

    return graph

def get_annotations(tablename, annotations):
    gene1 = {"name": "gene1", "start": 1000, "end": 2000}
    gene2 = {"name": "gene2", "start": 6000, "end": 10000}

    return [gene1, gene2]



def get_bubbles(bubble, bubble_inside, bubbles, graph, chr=None, start=None, end=None):
    
    rows = bubble.query.all()

    for row in rows:
        
        bid = "bubble_" + str(row.id)
        inside = bubble_inside.query.filter_by(bubble_id=row.id).all()

        subgraph = []
        for e in inside:
            subgraph.append(graph[e.node_id])

        bubbles[bid] = Bubble(bid, graph[row.start], graph[row.end], subgraph, 
                group=int(row.id), description="desc", size=5)

    return bubbles
