class SimpleLink:
    def __init__(self, row):
        self.fromNodeId = row.from_id
        self.toNodeId = row.to_id

        self.fromStrand = row.from_strand
        self.toStrand = row.to_strand

        self.consumed = False
        self.pathCount = 0

    def consume(self):
        self.consumed = True
    def is_consumed(self):
        return self.consumed

    def countOne(self):
        self.pathCount+=1
    def getCount(self):
        return self.pathCount

    def __str__(self):
        return str(["link", {"source": self.fromNodeId, "target": self.toNodeId}])
    def __repr__(self):
        return str(["link", {"source": self.fromNodeId, "target": self.toNodeId}])
