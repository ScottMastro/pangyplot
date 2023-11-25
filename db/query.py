import db.neo4j_query as q

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

    chains,chainLinks = q.get_top_level_chains(chrom, start, end)
    bubbles,bubbleLinks = q.get_top_level_bubbles(chrom, start, end)
    segments,segmentLinks = q.get_top_level_segments(chrom, start, end)

    #segmentLinks = remove_bubble_insertion_link(bubbles, bubbleLinks, segmentLinks)

    graph = {"nodes": chains + bubbles + segments, 
             "links": chainLinks + bubbleLinks + segmentLinks}

    return graph

def get_annotations(chrom, start, end):
    annotations = q.get_annotation_range(chrom, start, end)
    return annotations

def get_subgraph(nodeid):
    type = "chain"
    if type == "bubble":
        segments,links = q.get_bubble_subgraph(nodeid)
        return {"nodes": segments, "links": links}

    elif type == "chain":
        nodes,links = q.get_chain_subgraph(nodeid)
        return {"nodes": nodes, "links": links}

    return {"nodes": [], "links": []}



