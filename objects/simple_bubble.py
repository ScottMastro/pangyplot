
class SimpleBubble:
    def __init__(self, row, insideRows):
        self.id = "bubble_" + str(row.id)

        self.sourceId = row.start
        self.sinkId = row.end
        self.chainId = row.chain_id
        self.type = row.type
        self.inside = []

        for insideRow in insideRows:
            self.inside.append(insideRow.node_id)

        self.parent = None
        self.children = set()

        self.annotations = []
        #for child in self.subgraph:
        #    self.annotations = list(set(self.annotations) | set(child.annotations))

    def isIndel(self):
        return self.type == "insertion"
    def isSnp(self):
        return self.type == "simple"


    def size(self):
        return len(self.inside)

    def add_parent(self, other):
        self.parent = other
        other.children.add(self)

    def subgraph_center(self):
        xcenter, ycenter = 0,0
        for segment in self.inside:
            x,y = segment.center()
            xcenter += x
            ycenter += y
        n=len(self.inside)
        return (xcenter/n, ycenter/n)

    def to_dict(self):
        return {"id": self.id, "source": self.source.id, "sink": self.sink.id, 
        "subgraph" : [x.id for x in self.subgraph]}

    def to_node_dict(self):
        center = self.subgraph_center()
        return [{"nodeid": self.id, "id": self.id, 
                "x": center[0]*XSCALE_NODE, "y": center[1], "group": self.group, \
                "description": self.description, "size": self.size, "annotations": self.annotations}]

    def to_link_dict(self):
        links = []

        sharedAnnotations = list(set(self.annotations) & set(self.source.annotations))
        links.append( {"source": self.source.sink_node_id(), "target": self.id,
            "group": self.group, "width": 1, "length":21, "type": "edge", "annotations": sharedAnnotations})

        sharedAnnotations = list(set(self.annotations) & set(self.sink.annotations))
        links.append( {"source": self.id, "target": self.sink.source_node_id(),
            "group": self.group, "width": 1, "length":21, "type": "edge", "annotations": sharedAnnotations})

        return links

    def __str__(self):
        return str(["bubble", self.id, self.type])

    def __repr__(self):
        return str(["bubble", self.id, self.type])


