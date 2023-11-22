import db.neo4j_query as q
from objects.simple_link import SimpleLink
from objects.simple_bubble import SimpleBubble
from objects.simple_annotation import SimpleAnnotation
from objects.simple_path import SimplePath

from db.model.link import Link
from db.model.annotation import Annotation
from db.model.bubble import Bubble,BubbleInside
from db.model.path import Path

XSCALE_NODE=1
KINK_SIZE=100
SEGMENT_WIDTH=21

def process_nodes(nodes):
    graphNodes = []
    graphLinks = []

    for node in nodes:
        isRef = "chrom" in node
        length = node["length"] if "length" in node else node["size"]
        n = int(length/KINK_SIZE) + 2
        for i in range(n):
            newNode = dict()
            newNode["id"] = f"{node['id']}_{i}" 
            newNode["isref"] = isRef
            newNode["nodeid"] = node["id"]
            for key in ["chrom" "start", "end"]:
                if key in node:
                    newNode[key] = node[key]

            if "x" in node and "y" in node:
                x = node["x"]
                y = node["y"]
            else:
                if n == 1: 
                    x = (node["x1"] + node["x2"])/2
                    y = (node["y1"] + node["y2"])/2
                else:
                    p = i / (n-1)
                    p = max(0, p) ; p = min(1,p)
                    x = p*node["x1"] + (1-p)*node["x2"]
                    y = p*node["y1"] + (1-p)*node["y2"]

            newNode["x"] = x
            newNode["y"] = y
            graphNodes.append(newNode)
        
            if i == 0: continue
            newLink = dict()
            newLink["source"] = f"{node['id']}_{i-1}"
            newLink["target"] = newNode["id"]
            newLink["type"] = "node"
            newLink["length"] = length/n
            newLink["width"] = SEGMENT_WIDTH
            graphLinks.append(newLink)

    return graphNodes, graphLinks

def get_segments(chrom, start, end):
    resultDict = dict()

    chains = q.get_top_level_chains(chrom, start, end)
    nodes,links = process_nodes(chains)
    resultDict["nodes"] = nodes
    resultDict["links"] = links

    bubbles = q.get_top_level_bubbles(chrom, start, end)
    nodes,links = process_nodes(bubbles)
    resultDict["nodes"].extend(nodes)
    resultDict["links"].extend(links)

    segments = q.get_top_level_segments(chrom, start, end)
    #print(chains)
    #print(bubbles)
    #print(segments)

    return resultDict

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