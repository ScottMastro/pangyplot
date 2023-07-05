
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

    def __str__(self):
        return str(["bubble", self.id, self.type])

    def __repr__(self):
        return str(["bubble", self.id, self.type])


