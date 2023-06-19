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

def annotate_graph(bubbles, graph):
    
    for bid in bubbles:
        bubble = bubbles[bid]
        for node in bubble.subgraph:
            graph[node.id].group += bubble.group

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
    annotations = []
    tracks = []


    #links.append({"source": "2048_0", "target": "2048_1",
    #                "group": 10, "width": 80, "length":100, "type": "annotation"})
    #links.append({"source": "2048_1", "target": "bubble_805",
    #                "group": 10, "width": 80, "length":100, "type": "annotation"})
    #links.append({"source": "bubble_805", "target": "2055_1",
    #                "group": 10, "width": 80, "length":100, "type": "annotation"})
    #links.append({"source": "2055_1", "target": "2055_0",
    #                "group": 10, "width": 80, "length":100, "type": "annotation"})
    #links.append({"source": "2055_0", "target": "bubble_804",
    #                "group": 10, "width": 80, "length":100, "type": "annotation"})
    #links.append({"source": "bubble_804", "target": "2058_1",
    #                "group": 10, "width": 80, "length":100, "type": "annotation"})
    #links.append({"source": "2058_1", "target": "2058_0",
    #                "group": 10, "width": 80, "length":100, "type": "annotation"})

    #bounding box
    example = {"type": "gene", "name": "example", "nodes":["415_0", "415_1", "417_0", "417_1", "420_0", "420_1", "423_0", "423_1",
    "428_0", "428_1", "430_0", "430_1", "432_0", "432_1", "436_0", "436_1","440_0", "440_1", "442_0", "442_1", "444_0", "444_1",]  }
    annotations.append(example)

    #track
    exampletrack = {"type": "gene", "name": "example", "nodes":["2017", "2111", "2115", "2118", "2121", "2126"]  }
    tracks.append(exampletrack)


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

        for n in newNodes:
            if nodeId in exampletrack["nodes"]:
                n["track"] = 1
            else:
                n["track"] =0


        for l in newLinks:
            if nodeId in exampletrack["nodes"]:
                l["track"] = 1
            else:
                l["track"] = 0
        nodes.extend(newNodes)
        links.extend(newLinks)




    resultDict = {"nodes": nodes, "links": links, "annotations": annotations, "tracks": tracks}

    #print(nodes)

    return resultDict
