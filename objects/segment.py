XSCALE_NODE=1
class PointerSegment:
    def __init__(self, id, pointTo):
        self.id = id
        self.point = pointTo

    def to_node_dict(self):
        return []
    def to_link_dict(self):
        return []

class SimpleBubble:
    def __init__(self, id, source, sink, subgraph=[], description="", size=1):

        self.id = id
        self.source = source
        self.sink = sink
        self.subgraph = subgraph
        
        self.group = 0
        self.description = description
        self.size = size
        self.parent = None 
        self.children = set()

        self.annotations = []
        for child in subgraph:
            self.annotations = list(set(self.annotations) | set(child.annotations))


    def add_parent(self, other):
        self.parent = other
        other.children.add(self)

    def subgraph_size(self):
        if len(self.subgraph) == 0:
            return 1
        return sum([x.subgraph_size() for x in self.subgraph])

    def subgraph_center(self):
        xcenter, ycenter = 0,0
        for segment in self.subgraph:
            x,y = segment.center()
            xcenter += x
            ycenter += y
        n=len(self.subgraph)
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
        return str(["bubble", {"source": self.source.id, "sink": self.sink.id}])

    def __repr__(self):
        return str(self.id)


