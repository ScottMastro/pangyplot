XSCALE_NODE=1
KINK_SIZE=100
SEGMENT_WIDTH=21

class SimpleSegment:
    def __init__(self, row):
        self.id = row.nodeid
        self.seq = row.seq[:10]
        self.length = len(row.seq)
        self.chrom, self.pos = row.chrom, row.pos
        self.start = row.pos if row.pos else None
        self.end = row.pos+self.length if row.pos else None
        self.x1, self.y1 = row.x1, row.y1
        self.x2, self.y2 = row.x2, row.y2
        self.annotations = []

    def get_type(self):
        return 1 if self.pos else 2

    def add_annotation(self, annotation):
        self.annotations.append(annotation)
    def get_annotation_ids(self):
        return [a.id for a in self.annotations]

    def center(self):
        if self.x1 is None:
            return None
        return ((self.x1+self.x2)/2, (self.y1+self.y2)/2)

    def get_distance(self):
        if self.x1 is None:
            return 1
        return ((self.x2 - self.x1)**2 + (self.y2 - self.y1)**2)**0.5

    def source_node_id(self):
        if self.length == 1:
            return self.id
        return str(self.id) + "_0"

    def sink_node_id(self):
        if self.length == 1:
            return self.id
        return self.id + "_1"

    def _mid_node_id(self,i):
        return self.id + "_mid"+str(i)

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

        return self._mid_node_id(i)

    def _create_node(self, i):
        node = dict()
        node["id"] = self._get_node_id(i)
        node["nodeid"] = self.id
        x,y = self._get_node_coord(i)
        node["x"] = x*XSCALE_NODE
        node["y"] = y
        node["size"] = 10
        node["group"] = self.get_type()
        node["chrom"] = self.chrom
        node["pos"] = self.pos
        node["start"] = self.start
        node["end"] = self.end
        node["length"] = self.length
        node["annotations"] = self.get_annotation_ids()
        return node

    def _create_link(self, i, j, length):
        link = dict()
        link["source"] = self._get_node_id(i)
        link["target"] = self._get_node_id(j)
        link["width"] = SEGMENT_WIDTH
        link["length"] = length
        link["type"] = "node"
        link["group"] = self.get_type()
        link["annotations"] = self.get_annotation_ids()
        return link


    def to_node_dict(self):

        nodes = []
        n = self.total_nodes()
        for i in range(n):
            node = self._create_node(i)
            nodes.append(node)
        return nodes

    def to_link_dict(self):

        links = []
        n = self.total_nodes()
        if n == 1: return []

        for i in range(n-1):
            length=self.get_distance()/n
            link = self._create_link(i, i+1, length=length)
            links.append(link)        

        return links
