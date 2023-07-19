LINK_WIDTH=1
LINK_LENGTH=10

DESTROY_LINK="DESTROY_LINK"

def source_node_id(id, segmentLookup):
    if id not in segmentLookup: return id
    return segmentLookup[id].source_node_id()
def sink_node_id(id, segmentLookup):
    if id not in segmentLookup: return id
    return segmentLookup[id].sink_node_id()

def create_link(fromId, toId, segmentLookup, annotations=[]):
    link = dict()
    link["source"] = source_node_id(fromId, segmentLookup)
    link["target"] = sink_node_id(toId, segmentLookup)
    link["width"] = LINK_WIDTH
    link["length"] = LINK_LENGTH
    link["type"] = "edge"
    link["group"] = 0
    link["annotations"] = annotations
    return link

def create_node(id, x, y, size=10, shape=0, annotations=[]):
    node = dict()
    node["id"] = id
    node["nodeid"] = id
    node["x"] = x
    node["y"] = y
    node["size"] = size
    node["shape"] = shape
    node["group"] = 3
    node["chrom"] = None
    node["pos"] = None
    node["start"] = None
    node["end"] = None
    node["length"] = None
    node["annotations"] = annotations
    return node

def approximate_position(node, startSegmentId, endSegmentId, segmentLookup):
    #todo: FIXME
    node["start"] = segmentLookup[startSegmentId].start
    node["end"] = segmentLookup[endSegmentId].end

    #print("start", startSegmentId, segmentLookup[startSegmentId].start, segmentLookup[startSegmentId].end)
    #print("end", endSegmentId, segmentLookup[endSegmentId].start, segmentLookup[endSegmentId].end)

    if node["start"] == node["end"]:
        node["pos"] = node["start"]

    node["chrom"] = "???"
    if segmentLookup[startSegmentId].chrom == segmentLookup[endSegmentId].chrom:
        node["chrom"] = segmentLookup[startSegmentId].chrom

    return node

class SimpleGraph:
    def __init__(self, bubble, subgraphs):
        self.linkFromId = None if bubble is None else bubble.sourceId
        self.linkToId = None if bubble is None else bubble.sinkId
        self.subgraphs = subgraphs
        self.subgraphs.sort(key=lambda subgraph: -subgraph.size())
        self.totalSize = None
        self.parent = None
        self.process = []

        for subgraph in subgraphs:
            subgraph.set_parent(self)

    def size(self):
        if self.totalSize is None:
            self.totalSize = sum([subgraph.size() for subgraph in self.subgraphs])
        return self.totalSize
        
    def center(self):
        xcenter, ycenter = 0,0
        n = 0
        for subgraph in self.subgraphs:
            x,y,m = subgraph.center()
            n += m
            xcenter += x*m
            ycenter += y*m
        return (xcenter/n, ycenter/n)

    def get_annotations(self, segmentLookup):
        annotations = []
        for subgraph in self.subgraphs:
            annotations.extend(subgraph.get_annotations(segmentLookup))
        return annotations

    def to_dictionary(self, segmentLookup, allLinks=False):
        result = {"nodes":[], "links":[]}

        for subgraph in self.subgraphs:
            subresult = subgraph.to_dictionary(segmentLookup)
            result["nodes"].extend(subresult["nodes"])
            result["links"].extend(subresult["links"])

        return result

    def get_parent(self):
        return self.parent

    def set_parent(self, parent):
        self.parent = parent

    def post_process(self):
        processes = self.process
        for subgraph in self.subgraphs:
            processes.extend(subgraph.post_process())
        return processes

    def __repr__(self):
        return str(self.subgraphs)

class SimpleIndelGraph(SimpleGraph):
    def __init__(self, bubble, atomicGraphs):
        super().__init__(bubble, atomicGraphs)
        self.bubbleId = bubble.id

    def to_dictionary(self, segmentLookup, allLinks=False):
        result = super().to_dictionary(segmentLookup, allLinks)

        annotations = self.get_annotations(segmentLookup)

        indelId = self.bubbleId + "_indel"
        x,y = self.center()
        indelNode = create_node(indelId, x, y, shape=2, annotations=annotations)
        result["nodes"].append(indelNode)

        indelLink1 = create_link(self.linkToId, indelId, segmentLookup, annotations=annotations)
        indelLink2 = create_link(indelId, self.linkFromId, segmentLookup, annotations=annotations)

        result["links"].append(indelLink1)
        result["links"].append(indelLink2)

        self.process.append([
            DESTROY_LINK,
            source_node_id(self.linkToId, segmentLookup),
            sink_node_id(self.linkFromId, segmentLookup)])
            
        return result

    def __repr__(self):
        return str(["indel", "from:", self.linkFromId, "to:", self.linkToId])

class SimpleSnpGraph(SimpleGraph):
    def __init__(self, bubble, atomicGraphs):
        super().__init__(bubble, atomicGraphs)
        self.bubbleId = bubble.id

    def to_dictionary(self, segmentLookup, allLinks=False):
        expand_nodes = []
        expand_links = []
        for subgraph in self.subgraphs:
            subresult = subgraph.to_dictionary(segmentLookup, allLinks=True)
            expand_nodes.extend(subresult["nodes"])
            expand_links.extend(subresult["links"])

        annotations = self.get_annotations(segmentLookup)
        x,y = self.center()
        bubbleNode = create_node(self.bubbleId, x, y, annotations=annotations)
        bubbleNode = approximate_position(bubbleNode, self.linkFromId, self.linkToId, segmentLookup)
        bubbleNode["expand_nodes"] = expand_nodes
        bubbleNode["expand_links"] = expand_links

        links = []
        links.append(create_link(self.linkToId, self.bubbleId, segmentLookup, annotations=annotations))
        links.append(create_link(self.bubbleId, self.linkFromId, segmentLookup, annotations=annotations))

        result = {"nodes": [bubbleNode], "links": links}
        return result

    def __repr__(self):
        return str(["snp", "from:", self.linkFromId, "to:", self.linkToId])

class SimpleAtomicGraph(SimpleGraph):
    def __init__(self, node, toLinks, fromLinks):
        super().__init__(None, [])

        self.node = node
        self.linksFrom = fromLinks
        self.linksTo = toLinks
        self.totalSize = 1

    def get_annotations(self, segmentLookup):
        annotations = self.node.get_annotation_ids()

        fromAnnotations = []
        for link in self.linksFrom:
            node = segmentLookup[link.fromNodeId]
            fromAnnotations.extend(node.get_annotation_ids())

        toAnnotations = []
        for link in self.linksTo:
            node = segmentLookup[link.toNodeId]
            toAnnotations.extend(node.get_annotation_ids())

        intersection = list(set(fromAnnotations) & set(toAnnotations))
        return annotations + intersection


    def _to_link_dict(self, segmentLookup, allLinks):
        links = self.node.to_link_dict()

        linkSet = self.linksTo
        if allLinks: linkSet = self.linksTo + self.linksFrom
        for l in linkSet:
            if l.is_consumed():
                continue
            link = create_link(l.fromNodeId, l.toNodeId, segmentLookup)
            l.consume()
            links.append(link)
            
        return links

    def center(self):
        x,y = self.node.center()
        return [x,y,1]

    def to_dictionary(self, segmentLookup, allLinks=False):
        nodes = self.node.to_node_dict()
        links = self._to_link_dict(segmentLookup, allLinks)

        result = {"nodes": nodes, "links": links}
        return result

    def __repr__(self):
        return str(["atomic", self.node.id, "fromlinks:", len(self.linksFrom),
        "tolinks:", len(self.linksTo)])
