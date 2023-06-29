def group_bubbles(bubbles):
    bubble_dict = {}

    def remove_from_bubble_dict(bid):
        for segment in bubbles[bid].subgraph:
            bubble_dict[segment.id].remove(bid)

    def is_contained(smaller, larger):
        return all(x in larger.subgraph for x in smaller.subgraph)

    for bid in bubbles:
        bubble = bubbles[bid]
        for node in bubble.subgraph:
            if node.id not in bubble_dict:
                bubble_dict[node.id] = []
            bubble_dict[node.id].append(bid)

    for id in bubble_dict:

        if len(bubble_dict[id]) > 1:

            sortedBids = sorted(bubble_dict[id], key=lambda x: len(bubbles[x].subgraph))
            
            i=0
            while len(sortedBids) > i+1:
                smallest = sortedBids[i]
                for bid in sortedBids[i+1:]:
                    if is_contained(bubbles[smallest], bubbles[bid]):
                        bubbles[smallest].add_parent(bubbles[bid])
                        #print(str(bid) +" is parent to " + str(smallest))
                        remove_from_bubble_dict(smallest)
                        break
                i+=1

    return bubbles


def add_annotations(annotations, graph):
    for annotation in annotations:
        for key in graph:
            segment = graph[key]
            if segment.pos is None:
                continue
            if annotation["start"] <= segment.pos and \
                annotation["end"] >= (segment.pos + segment.length):
                segment.add_annotation(annotation["index"])

    return graph

def get_graph_dictionary(graph, bubbles, annotations):

    nodesDone = set()

    def bubble_dict(bubble):
        
        nodes = []
        links = []
        ids = set()
        resultDict = {"children": []}
        for child in bubble.children:
            childDict, cids = bubble_dict(child)
            ids.update(cids)
            resultDict["children"].append(childDict)

        for segment in bubble.subgraph:
            id = segment.id
            if id in ids: continue
            ids.add(id)
            nodes.extend(segment.to_node_dict())
            links.extend(segment.to_link_dict())
            links.extend(segment.get_external_link_dict())
            links.extend(segment.from_links_dict(remember=True, excludeIds=ids))
            nodesDone.add(segment.id)

            resultDict["expand_nodes"] = nodes
            resultDict["expand_links"] = links

        resultDict["nodes"] = bubble.to_node_dict()
        resultDict["nodes"][0]["expand_nodes"] = resultDict["expand_nodes"]
        resultDict["nodes"][0]["expand_links"] = resultDict["expand_links"]

        resultDict["links"] = bubble.to_link_dict()

        return [resultDict, ids]

    #top level graph
    nodes = []
    links = []

    bubbleDict = []

    for bid in bubbles:
        if bubbles[bid].parent is None:
            d,ids = bubble_dict(bubbles[bid])

            bubbleDict.append(d)
            nodes.extend(d["nodes"])
            links.extend(d["links"])

    for nodeId in graph:
        if nodeId in nodesDone:
            continue
        newNodes = graph[nodeId].to_node_dict()
        newLinks = graph[nodeId].to_link_dict()


        nodes.extend(newNodes)
        links.extend(newLinks)

    resultDict = {"nodes": nodes, "links": links, "annotations": annotations}

    #print(nodes)

    return resultDict
