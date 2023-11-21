from db.db import db

class Bubble(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chain_id = db.Column(db.Integer)
    type = db.Column(db.String)
    start = db.Column(db.String)
    end = db.Column(db.String)

    def __init__(self, row):
        self.id = int(row["id"])
        self.chain_id = int(row["chain_id"])        
        self.type = row["type"]
        self.start = str(row["start"])
        self.end = str(row["end"])
        
    def __repr__(self):
        return self.type + "\t" + str(self.id) + "\t[" + str(self.start) + ", " + str(self.end) + "]"

class BubbleInside(db.Model):
    id = db.Column(db.String, primary_key=True)
    node_id = db.Column(db.String)
    bubble_id = db.Column(db.Integer)

    def __init__(self, row):
        self.id = str(row["id"]) + "_" + str(row["bubble_id"])
        self.node_id = str(row["id"])
        self.bubble_id = int(row["bubble_id"])        
        
    def __repr__(self):
        return str(self.id) + " -> " + str(self.bubble_id)