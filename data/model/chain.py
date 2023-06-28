from data.db import db

class Chain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)
    parent_sb = db.Column(db.Integer)
    parent_chain = db.Column(db.Integer)

    def __init__(self, id, start, end, parent_sb, parent_chain):
        self.id = int(id)
        self.start = int(start)
        self.end = int(end)
        self.parent_sb = None if parent_sb is None else int(parent_sb)
        self.parent_chain = None if parent_chain is None else int(parent_chain)

    def __repr__(self):
        return str(self.id) + "\t[" + str(self.start) + ", " + str(self.end) + "]"
