from math import floor

XSCALE_NODE=1
KINK_SIZE=100

def createNode(segment, id, x, y):
    node = dict()
    node["id"] = id
    node["nodeid"] = segment.id
    node["x"] = x*XSCALE_NODE
    node["y"] = y
    node["size"] = 3
    node["group"] = segment.get_type()
    node["chrom"] = segment.chrom
    node["pos"] = segment.pos
    node["start"] = segment.start
    node["end"] = segment.end
    node["length"] = segment.length
    node["annotations"] = segment.annotations
    return node

def createLink(source, sink, type, group, width, length):
    link = dict()
    sharedAnnotations = list(set(source.annotations) & set(sink.annotations))
    link["source"] = source.source_node_id()
    link["target"] = sink.sink_node_id()
    link["width"] = width
    link["length"] = length
    link["type"] = type
    link["group"] = group
    link["annotations"] = sharedAnnotations

    return link

class SimpleSegment:
    def __init__(self, row):
        self.id = str(row.nodeid)

        self.seq = row.seq[:10]
        self.length = len(row.seq)

        self.chrom, self.pos = row.chrom, row.pos

        self.start = row.pos if row.pos else None
        self.end = row.pos+self.length if row.pos else None

        self.x1, self.y1 = row.x1, row.y1
        self.x2, self.y2 = row.x2, row.y2

        self.link_to = []
        self.link_from = []
        self.remember_link_from = []
        
        self.annotations = []

    def get_type(self):
        return 1 if self.pos else 2

    def center(self):
        if self.x1 is None:
            return None
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
        n=floor(self.length/KINK_SIZE)
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
            x, y = self.center()
            node = createNode(self, self.id, x, y)
            return [node]

        else:
            middle_nodes =[]
        
            for i,mid in enumerate(self.get_mid_coords()):
                node = createNode(self, self.mid_node_id(i), mid[0], mid[1])
                middle_nodes.append(node)

            node_source = createNode(self, self.source_node_id(), self.x1, self.y1)
            node_sink = createNode(self, self.sink_node_id(), self.x2, self.y2)

            return [node_source] + middle_nodes + [node_sink]

    def to_link_dict(self, all=False):
        links = []


        if self.length == 1:
            for other in self.link_to:
                if all or other.id not in self.remember_link_from:
                    link = createLink(self, other, type="edge", group=self.get_type(), width=1, length=1, )
                    links.append(link)

        else:

            midcoords=self.get_mid_coords()

            if len(midcoords) > 0:
                LEN=self.get_distance()/(len(midcoords)+1)

                links.append( {"source": self.source_node_id(), "target": self.mid_node_id(0),
                "group": self.get_type(), "width": 21, "length":LEN, "type": "node", "annotations": self.annotations} )
                links.append( {"source": self.mid_node_id(len(midcoords)-1), "target": self.sink_node_id(),
                "group": self.get_type(), "width": 21, "length":LEN, "type": "node", "annotations": self.annotations} )

                for i,mid in enumerate(midcoords[:-1]):
                    links.append( {"source": self.mid_node_id(i), "target": self.mid_node_id(i+1),
                    "group": self.get_type(), "width": 21, "length":LEN, "type": "node", "annotations": self.annotations} )

            else:
                links.append( {"source": self.source_node_id(), "target": self.sink_node_id(),
                    "group": self.get_type(), "width": 21, "length":self.get_distance(), "type": "node", "annotations": self.annotations} )

            for other in self.link_to:
                if all or other.id not in self.remember_link_from:

                    sharedAnnotations = list(set(self.annotations) & set(other.annotations))
                    links.append( {"source": self.source_node_id(), "target": other.sink_node_id(),
                        "group": self.get_type(), "width": 1, "length":1, "type": "edge", "annotations": sharedAnnotations})
            
        return links

    def from_links_dict(self, remember=False, excludeIds=set()):
        links = []

        for other in self.link_from:

            sharedAnnotations = list(set(self.annotations) & set(other.annotations))

            if other.id not in excludeIds:
                links.append( {"source": other.source_node_id(), "target": self.sink_node_id(),
                    "group": self.get_type(), "width": 1, "length":1, "type": "edge", "annotations": sharedAnnotations})
                if remember:
                    other.remember_link_from.append(self.id)
        return links


    def __str__(self):
        return str(["segment", {"source": self.source_node_id(), "target": self.sink_node_id()}])

