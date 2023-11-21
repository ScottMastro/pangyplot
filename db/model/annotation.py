from db.db import db

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

    def __init__(self, row):
        self.id = str(row["id"])
        self.aid = str(row["aid"])
        self.chrom = str(row["chrom"])
        self.start = str(row["start"])
        self.end = str(row["end"])
        self.source = str(row["source"])
        self.type = str(row["type"])
        self.gene = str(row["gene"])
        self.info = str(row["info"])

    def __repr__(self):
        return "\t".join([str(x) for x in [self.id, self.type, self.chrom, self.start, self.end]])
