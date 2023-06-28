from data.db import db

class BubbleInside(db.Model):
    id = db.Column(db.String, primary_key=True)
    node_id = db.Column(db.String)
    bubble_id = db.Column(db.Integer)

    def __init__(self, id, bubble_id):
        self.id = str(id) + "_" + str(bubble_id)
        self.node_id = str(id)
        self.bubble_id = int(bubble_id)        
        
    def __repr__(self):
        return str(self.id) + " -> " + str(self.bubble_id)
