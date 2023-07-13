from data.db import db

def strand2bin(strand):
    return 1 if strand == "+" else 0
def bin2strand(strand):
    return "+" if strand == 1 else "-"

class Path(db.Model):
    id = db.Column(db.String, primary_key=True)
    next_id = db.Column(db.String)
    strand = db.Column(db.Boolean)

    def __init__(self, row):
        pass

    def __repr__(self):
        return [self.id, bin2strand(self.next_id), self.strand]

