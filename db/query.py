import db.neo4j_query as q
from db.query_top_level import get_top_level, get_top_level_segments

def remove_bubble_insertion_link(bubbles, bubbleLinks, segmentLinks):
    sourceDict, targetDict = dict(), dict()
    
    for link in segmentLinks+bubbleLinks:
        source, target = link["source"], link["target"]
        if source not in sourceDict: sourceDict[source] = []
        sourceDict[source].append(target)
        if target not in targetDict: targetDict[target] = []
        targetDict[target].append(source)

    toRemove = dict()
    for bubble in bubbles:
        if bubble["subtype"] != "insertion":
            continue

        bid = bubble["nodeid"]
        for source in targetDict[bid]:
            for target in sourceDict[bid]:
                if target in sourceDict[source]:
                    toRemove[source]=target

    filteredLinks = []
    for link in segmentLinks:
        if link["source"] in toRemove and link["target"] == toRemove[link["source"]]:
            continue
        filteredLinks.append(link)

    return filteredLinks

def get_segments(chrom, start, end):

    nodes,links = get_top_level(chrom, start, end)
    segments,segmentLinks = get_top_level_segments(chrom, start, end)

    #segmentLinks = remove_bubble_insertion_link(bubbles, bubbleLinks, segmentLinks)

    graph = {"nodes": nodes + segments, 
             "links": links + segmentLinks}

    return graph

def get_annotations(chrom, start, end):
    annotations = q.get_annotation_range(chrom, start, end)
    return annotations

def get_subgraph(nodeid):
    segments,links = q.get_subgraph(nodeid)
    return {"nodes": segments, "links": links}



