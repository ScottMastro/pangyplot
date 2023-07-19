from data.db import db

def strand2bin(strand):
    return 1 if strand == "+" else 0
def bin2strand(strand):
    return "+" if strand == 1 else "-"

class Path(db.Model):
    id = db.Column(db.String, primary_key=True)
    sample = db.Column(db.String)
    hap = db.Column(db.Integer)
    from_id = db.Column(db.String)
    to_id = db.Column(db.String)
    strand = db.Column(db.Boolean)

    def __init__(self, row):
        hp = "" if row["hap"] is None else "." + str(row["hap"])
        self.id = row["sample"] + hp + "." + str(row["i"]) 

        self.sample = row["sample"]
        self.hap = row["hap"]

        self.from_id = row["from_id"]
        self.to_id = row["to_id"]
        self.strand = strand2bin(row["strand"])

    def __repr__(self):
        return [self.id, bin2strand(self.next_id), self.strand]

