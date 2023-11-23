import db.neo4j_query as q

XSCALE_NODE=1
KINK_SIZE=100
SEGMENT_WIDTH=21
MIN_SIZE_SINGLE_NODE=6

def get_nodeid(id, n, i):
    if n==1:
        return str(id) 
    if i == 0:
        return f"{id}#0" 
    if i == n-1:
        return f"{id}#1"

    return f"{id}#m{i}"


def process_nodes(nodes, type):
    graphNodes = []
    graphLinks = []

    for node in nodes:
        length = node["length"] if "length" in node else node["size"]
        n = int(length/KINK_SIZE) + 2
        if length < MIN_SIZE_SINGLE_NODE:
            n=1
        for i in range(n):
            newNode = dict()

            if i == 0 or i == n-1:
                newNode["class"] = "end"
            else:
                newNode["class"] = "mid"

            newNode["type"] = type

            # TODO: remove
            if "type" in node:
                newNode["subtype"] = node["type"]


            newNode["id"] = str(node["id"])
            newNode["nodeid"] = get_nodeid(node["nodeid"], n, i)

            newNode["isref"] = "chrom" in node

            for key in ["chrom" "start", "end", "subtype"]:
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
            newLink["source"] = get_nodeid(node["nodeid"], n, i-1)
            newLink["target"] = newNode["nodeid"]
            newLink["class"] = "node"
            newLink["type"] = type
            newLink["length"] = length/n
            newLink["width"] = SEGMENT_WIDTH
            graphLinks.append(newLink)

    return graphNodes, graphLinks

def process_links(links):
    graphLinks = []
    for link in links:
        newLink = dict()
        newLink["source"] = str(link["source"])+"#1"
        newLink["target"] = str(link["target"])+"#0"
        newLink["sourceid"] = str(link["source"])
        newLink["targetid"] = str(link["target"])
        newLink["class"] = "edge"
        newLink["length"] = 10
        newLink["width"] = 4
        graphLinks.append(newLink)

    return graphLinks


def process_node_links(nodes, links):
    nodeids = {n["nodeid"] for n in nodes}
    sourceDict, targetDict = dict(), dict()
    
    for i,link in enumerate(links):
        if link["class"] != "edge":
            continue
        source, target = link["sourceid"], link["targetid"]
        if source not in sourceDict: sourceDict[source] = []
        sourceDict[source].append(target)
        if target not in targetDict: targetDict[target] = []
        targetDict[target].append(source)

    toRemove = dict()
    for node in nodes:
        if node["type"] != "bubble":
            continue
        if "subtype" not in node or node["subtype"] != "insertion":
            continue
        
        bid = node["nodeid"].split("#")[0]
        for source in targetDict[bid]:
            for target in sourceDict[bid]:
                if target in sourceDict[source]:
                    toRemove[source]=target
    
    newLinks = []
    for i,link in enumerate(links):
        if link["class"] == "edge":
            if link["sourceid"] in toRemove:
                if link["targetid"] in toRemove[link["sourceid"]]:
                    continue

        if link["source"] not in nodeids:
            prefix = link["source"].split("#")[0]
            if prefix in nodeids:
                links[i]["source"] = prefix
            else:
                # TODO: handle
                print("WARNING: MISSING NODE ", link["source"])
        if link["target"] not in nodeids:
            prefix = link["target"].split("#")[0]
            if prefix in nodeids:
                links[i]["target"] = prefix
            else:
                # TODO: handle
                print("WARNING: MISSING NODE ", link["target"])
        
        newLinks.append(link)

    return nodes, newLinks

def get_segments(chrom, start, end):
    allNodes = []
    allLinks = []

    chains,links = q.get_top_level_chains(chrom, start, end)
    nodes,nodelinks = process_nodes(chains, "chain")
    links = process_links(links)
    allNodes.extend(nodes)
    allLinks.extend(nodelinks)
    allLinks.extend(links)

    bubbles,links = q.get_top_level_bubbles(chrom, start, end)
    nodes,nodelinks = process_nodes(bubbles, "bubble")
    links = process_links(links)
    allNodes.extend(nodes)
    allLinks.extend(nodelinks)
    allLinks.extend(links)

    segments,links = q.get_top_level_segments(chrom, start, end)
    nodes,nodelinks = process_nodes(segments, "segment")
    links = process_links(links)
    allNodes.extend(nodes)
    allLinks.extend(nodelinks)
    allLinks.extend(links)


    allNodes, allLinks = process_node_links(allNodes, allLinks)
    graph = {"nodes": allNodes, "links": allLinks}

    #print(graph)
    return graph
    
def get_subgraph(type, id):
    allNodes = []
    allLinks = []

    if type == "bubble":
        segments,links = q.get_bubble_subgraph(id)
        nodes,nodelinks = process_nodes(segments, "segment")
        links = process_links(links)
        allNodes.extend(nodes)
        allLinks.extend(nodelinks)
        allLinks.extend(links)

    elif type == "chain":
        q.get_chain_subgraph(id)

    subgraph = {"nodes": allNodes, "links": allLinks}
    return subgraph