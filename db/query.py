import db.neo4j_query as q
from objects.simple_link import SimpleLink
from objects.simple_bubble import SimpleBubble
from objects.simple_annotation import SimpleAnnotation
from objects.simple_path import SimplePath

from db.model.link import Link
from db.model.annotation import Annotation
from db.model.bubble import Bubble,BubbleInside
from db.model.path import Path

def get_segments(chrom, start, end):
    result = q.get_segments(chrom, start, end)    
    return result

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

def get_haplotypes(linkDict, chrom, start, end):

    rows = Path.query.filter(
        Path.chrom == chrom, 
        Path.start >= start,
        Path.end <= end
    ).all()

    def find_link(row):
        if row.from_id not in linkDict: 
            return None
        for link in linkDict[row.from_id]:
            if link.toNodeId == row.to_id:
                return link
        return None

    paths = dict()
    for row in rows:
        link = find_link(row)
        sample = row.sample + "." + str(0 if row.hap is None else row.hap)
        if sample not in paths:
            paths[sample] = SimplePath(row)

        paths[sample].add_to_path(link)

    return paths