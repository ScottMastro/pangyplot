from objects.simple_segment import SimpleSegment
from objects.simple_link import SimpleLink
from objects.simple_bubble import SimpleBubble

from data.model.segment import Segment
from data.model.link import Link
from data.model.annotation import Annotation
from data.model.bubble import Bubble,BubbleInside

def get_node_dict(chr=None, start=None, end=None):
    #todo: filter by chrom:pos somehow
    nodes = dict()

    rows = Segment.query.all()
    for row in rows:
        node = SimpleSegment(row)
        nodes[str(row.nodeid)] = node
    
    return nodes

def get_link_dict(chr=None, start=None, end=None):
    toDict = dict()
    fromDict = dict()

    rows = Link.query.all()
    for row in rows:
        link = SimpleLink(row)
        if link.toNodeId not in toDict:
            toDict[link.toNodeId] = []
        if link.fromNodeId not in fromDict:
            fromDict[link.fromNodeId] = []

        toDict[link.toNodeId].append(link)
        fromDict[link.fromNodeId].append(link)

    return toDict,fromDict

def get_bubble_list(chr=None, start=None, end=None):
    
    rows = Bubble.query.all()
    bubbleList = []
    for row in rows:
        insideRows = BubbleInside.query.filter_by(bubble_id=row.id).all()

        bubble = SimpleBubble(row, insideRows)
        bubbleList.append(bubble)

    return bubbleList


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
