from data.db import db

class Segment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nodeid = db.Column(db.String)

    seq = db.Column(db.String)
    x1 = db.Column(db.Float)
    y1 = db.Column(db.Float)
    x2 = db.Column(db.Float)
    y2 = db.Column(db.Float)
    chrom = db.Column(db.String)
    pos = db.Column(db.Integer)
    length = db.Column(db.Integer)
    ref = db.Column(db.Boolean)

    component = db.Column(db.Integer)
    
    chrom_pos_index = db.Index("chrom_pos_index", "chrom", "pos")

    def __init__(self, row):

        self.id = row["id"]
        self.nodeid = str(row["nodeid"])
        self.seq = row["seq"]
        self.chrom = row["chrom"]
        self.pos = row["pos"]
        self.length = len(row["seq"])
        self.ref = row["ref"]

        self.x1 = None
        self.y1 = None
        self.x2 = None
        self.y2 = None

    def update_layout(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        db.session.commit()

    def __repr__(self):
        sequence = self.seq[:min(10,len(self.seq))].strip()
        if len(self.seq) > 10: 
            sequence += "\t...(+" +str(len(self.seq)-10) + " bases)" 
        else:
            sequence += "\t\t\t"

        coords = " -> (" + str(round(self.x1)) + "," + str(round(self.y2)) + "), " + \
            "(" + str(round(self.x2)) + "," + str(round(self.y2)) + ")"
        return str(self.id) + "\t" + sequence + "\t" + coords