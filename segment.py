
from math import floor
from re import S

class Segment:
    def __init__(self, segId, group=0, description="", size=1, subgraph=[]):
        self.id = segId
        self.description = description
        self.group = group
        self.size = size
        self.link_to = []
        self.link_from = []
        self.x1 = None ; self.y1 = None
        self.x2 = None ; self.y2 = None
        
        self.parent = None
        self.subgraph = subgraph
        for sg in subgraph:
            sg.parent = self

    def add_source_node(self, xpos, ypos):
        self.x1 = xpos
        self.y1 = ypos
    def add_sink_node(self, xpos, ypos):
        self.x2 = xpos
        self.y2 = ypos

    def add_to_subgraph(self, other):
        self.subgraph.append(other)
    def subgraph_size(self):
        if len(self.subgraph) == 0:
            return 1
        return sum([x.subgraph_size() for x in self.subgraph])

    def subgraph_center(self):
        if len(self.subgraph) == 0:
            return ((self.x1+self.x2)/2, (self.y1+self.y2)/2)

        n = self.subgraph_size()
        xcenter, ycenter = 0,0
        for sg in self.subgraph:
            sx,sy = sg.subgraph_center()
            w = sg.subgraph_size()/n
            xcenter += sx * w
            ycenter += sy * w
        return (xcenter, ycenter)

    def source_node_id(self):
        if len(self.subgraph) > 0 :
            return self.id
        if self.parent is None:
            return self.id + "_0"
        else:
            return self.parent.source_node_id()
    def sink_node_id(self):
        if len(self.subgraph) > 0 :
            return self.id
        if self.parent is None:
            return self.id + "_1"
        else:
            return self.parent.source_node_id()

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

        if len(self.subgraph) > 0:
            center = self.subgraph_center()
            node = {"nodeid": self.id, "id": self.id, 
                "x": center[0], "y": center[1], "group": self.group, \
                "description": self.description, "size": self.size}
            return [node]

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

    def all_to_links(self):
        links_to = set()
        if len(self.subgraph) == 0:
            return set(self.link_to)
        for sg in self.subgraph:
            sublinks = sg.all_to_links()
            links_to.update(sublinks)
        return links_to

    def to_link_dict(self):
        links = []
        if len(self.subgraph) > 0:
            links_to = self.all_to_links()
            to_ids = set([link.sink_node_id() for link in links_to])
            for id in to_ids:
                links.append( {"source": self.source_node_id(), "target": id,
                "group": self.group, "width": 1, "length":30, "type": "node"} )

                            
            return links

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

