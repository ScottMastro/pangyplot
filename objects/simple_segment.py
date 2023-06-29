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

def createSelfLink(self, i, j, type, group, width, length):
    link = dict()
    link["source"] = self._get_node_id(i)
    link["target"] = self._get_node_id(j)
    link["width"] = width
    link["length"] = length
    link["type"] = type
    link["group"] = group
    link["annotations"] = self.annotations

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

    def center(self):
        if self.x1 is None:
            return None
        return ((self.x1+self.x2)/2, (self.y1+self.y2)/2)

    def total_nodes(self):
        if self.length == 1:
            return 1
        return int(self.length/KINK_SIZE) + 2

    def _get_node_coord(self, i):
        n = self.total_nodes()
        if n == 1: return self.center()

        p = i / (n-1)
        p = max(0, p) ; p = min(1,p)
        x = p*self.x1 + (1-p)*self.x2
        y = p*self.y1 + (1-p)*self.y2
        return (x,y)

    def _get_node_id(self, i):
        n = self.total_nodes()
        if n == 1: return self.id
        if i == 0: return self.source_node_id()
        if i == n-1: return self.sink_node_id()

        return self.mid_node_id(i)

    def to_node_dict(self):

        nodes = []
        n = self.total_nodes()
        for i in range(n):
            x,y = self._get_node_coord(i)
            id = self._get_node_id(i)

            node = createNode(self, id, x, y)
            nodes.append(node)
        return nodes


    def get_type(self):
        return 1 if self.pos else 2


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



    def get_kink_links(self):

        midcoords=self.get_mid_coords()
        links = []

        kinkLen=self.get_distance()

        link = createLink(self, self, type="node", group=self.get_type(), width=21, length=kinkLen)
        link["target"] = self.mid_node_id(0)
        links.append(link)

        link = createLink(self, self, type="node", group=self.get_type(), width=21, length=kinkLen)
        link["source"] = self.mid_node_id(len(midcoords)-1)
        links.append(link)

        for i,mid in enumerate(midcoords[:-1]):
            link = createLink(self, self, type="node", group=self.get_type(), width=21, length=kinkLen)
            link["source"] = self.mid_node_id(i)
            link["target"] = self.mid_node_id(i+1)
            links.append(link)
        
        return links

    def to_link_dict(self):

        links = []
        n = self.total_nodes()
        if n == 1: return []

        for i in range(n-1):
            length=self.get_distance()/n
            link = createSelfLink(self, i, i+1, type="node", group=self.get_type(), width=21, length=length)
            links.append(link)        

        return links

    def get_external_link_dict(self, all=False):

        links = []

        if self.length == 1:
            for other in self.link_to:
                if all or other.id not in self.remember_link_from:
                    link = createLink(self, other, type="edge", group=self.get_type(), width=1, length=1, )
                    links.append(link)
            return links
        
        #get self-links
        else:
            link = createLink(self, self, type="node", group=self.get_type(), width=21, length=self.get_distance(), )
            links.append(link)

        for other in self.link_to:
            if all or other.id not in self.remember_link_from:
                link = createLink(self, other, type="edge", group=self.get_type(), width=1, length=1, )
                links.append(link)

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

