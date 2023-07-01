class SimpleLink:
    def __init__(self, row):
        self.fromNodeId = row.from_id
        self.toNodeId = row.to_id

        self.fromStrand = row.from_strand
        self.toStrand = row.to_strand

        self.consumed = False

    def consume(self, info):
        self.consumed = True
    def is_consumed(self):
        return self.consumed

    def to_link_dict(self):

        links = []
        n = self.total_nodes()
        if n == 1: return []

        for i in range(n-1):
            length=self.get_distance()/n
            link = self._create_link(i, i+1, length=length)
            links.append(link)        

        return links

    def __str__(self):
        return str(["link", {"source": self.fromNodeId, "target": self.toNodeId}])
    def __repr__(self):
        return str(["link", {"source": self.fromNodeId, "target": self.toNodeId}])
