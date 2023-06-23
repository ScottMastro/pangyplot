from segment import SimpleSegment,Bubble

def get_nodes(segment, graph, chr=None, start=None, end=None):
    rows = segment.query.all()
    for row in rows:
        node = SimpleSegment(row.nodeid, group=3, description="desc", size=3,
        chrom=row.chrom, pos=row.pos, length=row.length)
        node.add_source_node(row.x1, row.y1)
        node.add_sink_node(row.x2, row.y2)
        graph[row.nodeid] = node

    return graph

def get_edges(link, graph, chr=None, start=None, end=None):
    rows = link.query.all()
    for row in rows:
        fromNode = graph[row.from_id]
        toNode = graph[row.to_id]
        fromNode.add_link_to(toNode)
        toNode.add_link_from(fromNode)

    return graph

def get_annotations(table, annotations, chromosome, start, end):

    rows = table.query.filter(
        table.chrom == chromosome,
        table.start >= start,
        table.end <= end
    ).all()
    
    for row in rows:
        d = {"index": row.id, "id": row.aid, "chrom": row.chrom, "start": row.start, "end": row.end,
        "type": row.type, "info": row.info}  
        annotations.append(d)

    return annotations


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
