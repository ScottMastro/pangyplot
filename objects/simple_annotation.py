class SimpleAnnotation:
    def __init__(self, row):
        self.id = row.id
        self.annotationId = row.aid
        self.chrom = row.chrom
        self.start = row.start
        self.end = row.end
        self.type = row.type
        self.info = row.info  
        self.gene = row.gene  

    def to_dict(self):
        result = {
            "index" : self.id,
            "id" : self.annotationId,
            "chrom" : self.chrom,
            "start" : self.start,
            "end" : self.end,
            "type" : self.type,
            "info" : self.info,
            "gene" : self.gene
        }
        return result
    
    def overlaps(self, segment):
        if segment.start is None or segment.end is None:
            return False
        return self.start <= segment.start and self.end >= segment.end

    def __str__(self):
        return str(["annotation", self.chrom, self.start, self.end, self.info])
    def __repr__(self):
        return str(["annotation", self.chrom, self.start, self.end, self.info])
