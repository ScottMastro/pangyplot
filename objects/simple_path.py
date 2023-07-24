class SimplePath:

    def __init__(self, row):
        self.sample = row.sample
        self.hap = row.hap
        self.links = []

    def add_to_path(self, link):
        self.links.append(link)

    def countPath(self):
        for link in self.links:
            if not link is None:
                link.countOne()

    def to_dict(self, linkDict):
        links = []
        return links

    def __repr__(self):
        info = [self.sample, "hap"+str(self.hap), len(self.links), "links"]
        return "\t".join([str(x) for x in info])

