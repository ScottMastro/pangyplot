def deduplicate_links(links):
    linkSet = set()
    dedup = []
    for link in links:
        key = (link["source"], link["target"])
        if key in linkSet:
            continue
        linkSet.add(key)
        dedup.append(link)
    return dedup

def deduplicate_nodes(nodes):
    nodeSet = set()
    dedup = []
    for node in nodes:
        if node is None or node["nodeid"] in nodeSet:
            continue
        nodeSet.add(node["nodeid"])
        dedup.append(node)
    return dedup

def remove_invalid_links(nodes, links, nodeids=None):
    if nodeids is None:
        nodeids={node["nodeid"] for node in nodes}
    keepLinks = []
    for link in links:
        if link["target"] not in nodeids or link["source"] not in nodeids:
            continue
        keepLinks.append(link)
    return keepLinks

