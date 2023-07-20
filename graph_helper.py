from objects.simple_graph import SimpleGraph,SimpleAtomicGraph,SimpleIndelGraph,SimpleSnpGraph
from objects.simple_graph import DESTROY_LINK

def construct_graph(segmentDict, toLinkDict, fromLinkDict, bubbleList):
    graphs = dict()
    for id in segmentDict:
        segment = segmentDict[id]
        toLinks = toLinkDict[id] if id in toLinkDict else []
        fromLinks = fromLinkDict[id] if id in fromLinkDict else []
        graphs[id] = SimpleAtomicGraph(segment, toLinks, fromLinks)
        

    bubbleList.sort(key=lambda bubble: bubble.size())
    for bubble in bubbleList:

        # use of arbitraryId assumes that a graph may only a be a subgraph
        # if it is completely contained in the parent graph
        arbitraryId = None
        subgraphs = []

        for id in bubble.inside:
            if id not in graphs:
                continue
            subgraphs.append(graphs.pop(id))
            arbitraryId = id
        if bubble.isIndel() or bubble.isSnp():
            if bubble.isIndel():
                graph = SimpleIndelGraph(bubble, subgraphs)
            elif bubble.isSnp():
                graph = SimpleSnpGraph(bubble, subgraphs)

            graphs[arbitraryId] = graph

        # not a snp or indel
        else:
            graph = SimpleGraph(bubble, subgraphs)
            graphs[arbitraryId] = graph

    totalGraph = SimpleGraph(None, [graphs[id] for id in graphs])
    return totalGraph

def post_process_graph(graph, graphDict):

    processes = graph.post_process()

    while len(processes) > 0:
        process = processes.pop()
        if process[0] == DESTROY_LINK:
            for i,link in enumerate(graphDict["links"]):
    
                if link["source"] == process[1] and link["target"] == process[2]:
                    graphDict["links"].pop(i)
                    break

    return graphDict

def add_annotations(annotations, segmentDict):
    for annotation in annotations:
        for key in segmentDict:
            segment = segmentDict[key]
            if segment.pos is None:
                continue
            if annotation.overlaps(segment):
                segment.add_annotation(annotation)

    return segmentDict

def process_paths(paths):

    for pathId in paths:
        paths[pathId].countPath()
