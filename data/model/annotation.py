from data.db import db

class Annotation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aid = db.Column(db.String)
    chrom = db.Column(db.String)
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)
    source = db.Column(db.String)
    type = db.Column(db.String)
    gene = db.Column(db.String)
    info = db.Column(db.String)

    def __init__(self, i, annotationId, chrom, start, end, source, type, gene, info):
        self.id = str(i)
        self.aid = str(annotationId)
        self.chrom = str(chrom)
        self.start = str(start)
        self.end = str(end)
        self.source = str(source)
        self.type = str(type)
        self.gene = str(gene)
        self.info = str(info)

    def __repr__(self):
        return "\t".join([str(x) for x in [self.id, self.type, self.chrom, self.start, self.end]])
