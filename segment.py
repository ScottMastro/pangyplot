
from math import floor

class Segment:
    def __init__(self, segId, group=0, description="", size=1):
        self.id = segId
        self.description = description
        self.group = group
        self.size = size
        self.link_to = []
        self.link_from = []

        self.subgraph = []

    def add_source_node(self, xpos, ypos):
        self.x1 = xpos
        self.y1 = ypos
    def add_sink_node(self, xpos, ypos):
        self.x2 = xpos
        self.y2 = ypos

    def source_node_id(self):
        return self.id + "_0"
    def sink_node_id(self):
        return self.id + "_1"
    def mid_node_id(self,i):
        return self.id + "_mid"+str(i)

    def get_distance(self):
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

    def to_link_dict(self):
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
            links.append( {"source": self.source_node_id(), "target": other.sink_node_id(),
                "group": self.group, "width": 1, "length":30, "type": "edge"})
        
        return links

    def __str__(self):
        return str(["segment", {"source": self.source_node_id(), "target": self.sink_node_id()}])
