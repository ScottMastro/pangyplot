
from math import floor

class PointerSegment:
    def __init__(self, id, pointTo):
        self.id = id
        self.point = pointTo

    def to_node_dict(self):
        return []
    def to_link_dict(self):
        return []

class Bubble:
    def __init__(self, id, source, sink, subgraph=[], group=0, description="", size=1):

        self.id = id
        self.source = source
        self.sink = sink
        self.subgraph = subgraph
        
        self.group = group
        self.description = description
        self.size = size
        self.parent = None 
        self.children = set() 

    def add_parent(self, other):
        self.parent = other
        other.children.add(self)

    def add_child(self, other):
        self.children.add(other)
        other.parent = self

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
                "x": center[0], "y": center[1], "group": self.group, \
                "description": self.description, "size": self.size}]

    def to_link_dict(self):
        links = []
        
        links.append( {"source": self.source.sink_node_id(), "target": self.id,
            "group": self.group, "width": 1, "length":30, "type": "edge"})
        links.append( {"source": self.id, "target": self.sink.source_node_id(),
            "group": self.group, "width": 1, "length":30, "type": "edge"})

        return links

    def __str__(self):
        return str(["bubble", {"source": self.source.id, "sink": self.sink.id}])

    def __repr__(self):
        return str(self.id)



class SimpleSegment:
    def __init__(self, id, group=0, description="", size=1):
        self.id = str(id)

        self.group = group
        self.description = description
        self.size = size
        
        self.x1 = None ; self.y1 = None
        self.x2 = None ; self.y2 = None
        
        self.link_to = []
        self.link_from = []
        
        self.remember_link_from = []

    def add_source_node(self, xpos, ypos):
        self.x1 = xpos
        self.y1 = ypos
    def add_sink_node(self, xpos, ypos):
        self.x2 = xpos
        self.y2 = ypos
    def center(self):
        return ((self.x1+self.x2)/2, (self.y1+self.y2)/2)

    def source_node_id(self):
        return str(self.id) + "_0"

    def sink_node_id(self):
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

    def to_node_dict(self):

        middle_nodes =[]

        for i,mid in enumerate(self.get_mid_coords()):
            middle_nodes.append({"nodeid": self.id, "id": self.mid_node_id(i), 
                "x": mid[0], "y": mid[1], "group": self.group, \
                "description": self.description, "size": 1})
    
        node1 = {"nodeid": self.id, "id": self.source_node_id(), 
                "x": self.x1, "y": self.y1, "group": self.group, \
                "description": self.description, "size": self.size}
        node2 = {"nodeid": self.id, "id": self.sink_node_id(), 
                "x": self.x2, "y": self.y2, "group": self.group, \
                "description": self.description, "size": self.size}
        return [node1, node2] + middle_nodes

    def to_link_dict(self, all=False):
        links = []

        midcoords=self.get_mid_coords()

        if len(midcoords) > 0:
            LEN=self.get_distance()/(len(midcoords)+1)

            links.append( {"source": self.source_node_id(), "target": self.mid_node_id(0),
            "group": self.group, "width": 10, "length":LEN, "type": "node"} )
            links.append( {"source": self.mid_node_id(len(midcoords)-1), "target": self.sink_node_id(),
            "group": self.group, "width": 10, "length":LEN, "type": "node"} )

            for i,mid in enumerate(midcoords[:-1]):
                links.append( {"source": self.mid_node_id(i), "target": self.mid_node_id(i+1),
                "group": self.group, "width": 10, "length":LEN, "type": "node"} )

        else:
            links.append( {"source": self.source_node_id(), "target": self.sink_node_id(),
                "group": self.group, "width": 10, "length":self.get_distance(), "type": "node"} )

        for other in self.link_to:
            if all or other.id not in self.remember_link_from:
                links.append( {"source": self.source_node_id(), "target": other.sink_node_id(),
                    "group": self.group, "width": 1, "length":30, "type": "edge"})
        
        return links

    def from_links_dict(self, remember=False, excludeIds=set()):
        links = []

        for other in self.link_from:
            if other.id not in excludeIds:
                links.append( {"source": other.source_node_id(), "target": self.sink_node_id(),
                    "group": self.group, "width": 1, "length":30, "type": "edge"})
                if remember:
                    other.remember_link_from.append(self.id)
        return links


    def __str__(self):
        return str(["segment", {"source": self.source_node_id(), "target": self.sink_node_id()}])

