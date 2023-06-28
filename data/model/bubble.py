from data.db import db

class Bubble(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chain_id = db.Column(db.Integer)

    type = db.Column(db.String)
    start = db.Column(db.String)
    end = db.Column(db.String)

    def __init__(self, id, chain_id, type, start, end):
        self.id = int(id)
        self.chain_id = int(chain_id)        
        self.type = type
        self.start = str(start)
        self.end = str(end)
        
    def __repr__(self):
        return self.type + "\t" + str(self.id) + "\t[" + str(self.start) + ", " + str(self.end) + "]"
