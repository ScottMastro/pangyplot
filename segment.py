from math import floor

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


XSCALE_NODE=1
def createNode(segment, id, x, y):
    return {"nodeid": segment.id, "id": id, 
            "x": x*XSCALE_NODE, "y": y, "group": segment.group, 
            "description": segment.description, "size": segment.size,
            "chrom": segment.chrom, "pos": segment.pos, "length": segment.length,
            "annotations": segment.annotations}


class SimpleSegment:
    def __init__(self, id, description="", size=1, chrom=None, pos=None, length=None):
        self.id = str(id)

        self.group = 0

        if pos is not None:
            self.group = 1

        self.description = description
        self.size = size
        
        self.x1 = None ; self.y1 = None
        self.x2 = None ; self.y2 = None
        
        self.link_to = []
        self.link_from = []
        
        self.remember_link_from = []

        self.chrom = chrom
        self.pos = pos
        self.length = length
        self.annotations = []

    def add_source_node(self, xpos, ypos):
        self.x1 = xpos
        self.y1 = ypos
    def add_sink_node(self, xpos, ypos):
        self.x2 = xpos
        self.y2 = ypos
    def center(self):
        return ((self.x1+self.x2)/2, (self.y1+self.y2)/2)

    def source_node_id(self):
        if self.length == 1:
            return self.id

        return str(self.id) + "_0"

    def sink_node_id(self):
        if self.length == 1:
            return self.id

        return self.id + "_1"

    def mid_node_id(self,i):
        return self.id + "_mid"+str(i)

    def get_distance(self):
        if self.x1 is None:
            return 1
        return ((self.x2 - self.x1)**2 + (self.y2 - self.y1)**2)**0.5

    def add_link_to(self, other):
        self.link_to.append(other)
    def add_link_from(self, other):
        self.link_from.append(other)

    def get_mid_coords(self):
        coords = []
        length = self.get_distance()
        n=floor(length/150)
        for i in range(n):
            p=(i+1)/(n+1)
            midx = p*self.x1 + (1-p)*self.x2
            midy = p*self.y1 + (1-p)*self.y2
            coords.append((midx, midy))
        return coords

    def add_annotation(self, annotationIndex):
        self.annotations.append(annotationIndex)

    def to_node_dict(self):

        if self.length == 1:
            node = createNode(self, self.id, self.x1, self.y1)
            return [node]

        else:
            middle_nodes =[]
        
            for i,mid in enumerate(self.get_mid_coords()):
                middle_nodes.append( createNode(self, self.mid_node_id(i), mid[0], mid[1]) )


            node1 = createNode(self, self.source_node_id(), self.x1, self.y1)
            node2 = createNode(self, self.sink_node_id(), self.x2, self.y2)

            return [node1, node2] + middle_nodes

    def to_link_dict(self, all=False):
        links = []


        if self.length == 1:
            for other in self.link_to:
                if all or other.id not in self.remember_link_from:

                    sharedAnnotations = list(set(self.annotations) & set(other.annotations))
                    links.append( {"source": self.source_node_id(), "target": other.sink_node_id(),
                        "group": self.group, "width": 1, "length":1, "type": "edge", "annotations": sharedAnnotations})


        else:

            midcoords=self.get_mid_coords()

            if len(midcoords) > 0:
                LEN=self.get_distance()/(len(midcoords)+1)

                links.append( {"source": self.source_node_id(), "target": self.mid_node_id(0),
                "group": self.group, "width": 21, "length":LEN, "type": "node", "annotations": self.annotations} )
                links.append( {"source": self.mid_node_id(len(midcoords)-1), "target": self.sink_node_id(),
                "group": self.group, "width": 21, "length":LEN, "type": "node", "annotations": self.annotations} )

                for i,mid in enumerate(midcoords[:-1]):
                    links.append( {"source": self.mid_node_id(i), "target": self.mid_node_id(i+1),
                    "group": self.group, "width": 21, "length":LEN, "type": "node", "annotations": self.annotations} )

            else:
                links.append( {"source": self.source_node_id(), "target": self.sink_node_id(),
                    "group": self.group, "width": 21, "length":self.get_distance(), "type": "node", "annotations": self.annotations} )

            for other in self.link_to:
                if all or other.id not in self.remember_link_from:

                    sharedAnnotations = list(set(self.annotations) & set(other.annotations))
                    links.append( {"source": self.source_node_id(), "target": other.sink_node_id(),
                        "group": self.group, "width": 1, "length":1, "type": "edge", "annotations": sharedAnnotations})
            
        return links

    def from_links_dict(self, remember=False, excludeIds=set()):
        links = []

        for other in self.link_from:

            sharedAnnotations = list(set(self.annotations) & set(other.annotations))

            if other.id not in excludeIds:
                links.append( {"source": other.source_node_id(), "target": self.sink_node_id(),
                    "group": self.group, "width": 1, "length":1, "type": "edge", "annotations": sharedAnnotations})
                if remember:
                    other.remember_link_from.append(self.id)
        return links


    def __str__(self):
        return str(["segment", {"source": self.source_node_id(), "target": self.sink_node_id()}])

