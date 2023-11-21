from db.db import db

def strand2bin(strand):
    return 1 if strand == "+" else 0
def bin2strand(strand):
    return "+" if strand == 1 else "-"

class Link(db.Model):
    id = db.Column(db.String, primary_key=True)
    from_strand = db.Column(db.Boolean)
    to_strand = db.Column(db.Boolean)
    from_id = db.Column(db.String)
    to_id = db.Column(db.String)
    #overlap = db.Column(db.String)

    def __init__(self, row):
        self.id = str(row["from_id"]) + row["from_strand"] + str(row["to_id"]) + row["to_strand"]
        self.from_id = str(row["from_id"])
        self.from_strand = strand2bin(row["from_strand"])
        self.to_id = str(row["to_id"])
        self.to_strand = strand2bin(row["to_strand"])

    def __repr__(self):
        info = [self.from_id, bin2strand(self.from_strand), self.to_id, bin2strand(self.to_strand)]
        return "\t".join([str(x) for x in info])
