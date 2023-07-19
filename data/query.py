from objects.simple_segment import SimpleSegment
from objects.simple_link import SimpleLink
from objects.simple_bubble import SimpleBubble
from objects.simple_annotation import SimpleAnnotation

from data.model.segment import Segment
from data.model.link import Link
from data.model.annotation import Annotation
from data.model.bubble import Bubble,BubbleInside

def get_segment_dict(chr=None, start=None, end=None):
    #todo: filter by chrom:pos somehow
    segments = dict()

    rows = Segment.query.all()
    for row in rows:
        segment = SimpleSegment(row)
        segments[str(row.nodeid)] = segment
    
    return segments

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


def get_annotation_list(chromosome, start, end):

    rows = Annotation.query.filter(
        Annotation.chrom == chromosome,
        Annotation.start >= start,
        Annotation.end <= end
    ).all()
    
    annotations=[]
    for row in rows:
        annotation = SimpleAnnotation(row)
        annotations.append(annotation)

    return annotations

def get_haplotypes(segmentDict):

    print(segmentDict)


    #todo: filter by chrom:pos somehow
    segments = dict()

    rows = Segment.query.all()
    for row in rows:
        segment = SimpleSegment(row)
        segments[str(row.nodeid)] = segment
    
    return segments
