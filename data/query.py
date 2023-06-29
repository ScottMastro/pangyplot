from objects.segment import SimpleBubble
from objects.simple_segment import SimpleSegment

from data.model.segment import Segment
from data.model.link import Link
from data.model.annotation import Annotation
from data.model.bubble import Bubble,BubbleInside

def get_nodes(graph, chr=None, start=None, end=None):
    #todo: filter by chrom:pos somehow
    rows = Segment.query.all()
    for row in rows:
        node = SimpleSegment(row)
        graph[row.nodeid] = node
    
    return graph

def get_edges(graph, chr=None, start=None, end=None):
    rows = Link.query.all()
    for row in rows:
        fromNode = graph[row.from_id]
        toNode = graph[row.to_id]
        fromNode.add_link_to(toNode)
        toNode.add_link_from(fromNode)

    return graph

def get_annotations(annotations, chromosome, start, end):

    rows = Annotation.query.filter(
        Annotation.chrom == chromosome,
        Annotation.start >= start,
        Annotation.end <= end
    ).all()
    
    for row in rows:
        d = {"index": row.id, "id": row.aid, "chrom": row.chrom, "start": row.start, "end": row.end,
        "type": row.type, "info": row.info}  
        annotations.append(d)

    return annotations

def get_bubbles(bubbles, graph, chr=None, start=None, end=None):
    
    rows = Bubble.query.all()

    for row in rows:
        
        bid = "bubble_" + str(row.id)
        inside = BubbleInside.query.filter_by(bubble_id=row.id).all()

        subgraph = []
        for e in inside:
            subgraph.append(graph[e.node_id])

        bubbles[bid] = SimpleBubble(bid, graph[row.start], graph[row.end], subgraph, 
                description="desc", size=5)

    return bubbles


'''

## ============================================================
## helpers
## ============================================================



def populate_all(app, gfa, tsv, bubble, gff3):
    gfa.populate_gfa(app, gfa)
    tsv.populate_tsv(app, tsv)
    json.populate_bubbles(app, bubble)
    #gff3.populate_annotations(app, gff3)

'''