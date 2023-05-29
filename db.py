from types import TracebackType
from unittest.result import failfast
from flask_sqlalchemy import SQLAlchemy
import sys
import json

db = SQLAlchemy()

def drop_all(app):

    drop(app, "gfa_link")
    drop(app, "gfa_segment")
    drop(app, "layout")
    drop(app, "bubble")
    drop(app, "chain")
    drop(app, "bubble_inside")


def init(app):
    db.init_app(app)
    
    #drop_all(app)

    with app.app_context():

        db.create_all()
        inspector = db.inspect(db.engine)

        for table_name in inspector.get_table_names():
            print(f"Table: {table_name}")
            for column in inspector.get_columns(table_name):
                print(f"- {column['name']}: {column['type']}")



class gfa_segment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seq = db.Column(db.String)

    def __init__(self, id, seq):
        self.id = int(id)
        self.seq = seq

    def __repr__(self):
        return str(self.id)

class gfa_link(db.Model):
    id = db.Column(db.String, primary_key=True)
    from_strand = db.Column(db.Boolean)
    to_strand = db.Column(db.Boolean)
    from_id = db.Column(db.Integer)
    to_id = db.Column(db.Integer)
    #overlap = db.Column(db.String)

    def __init__(self, from_id, from_strand, to_id, to_strand):
        self.id = str(from_id) + "_" + str(to_id)
        self.from_id = int(from_id)
        self.from_strand = strand2bin(from_strand)
        self.to_id = int(to_id)
        self.to_strand = strand2bin(to_strand)

    def __repr__(self):
        info = [self.from_id, bin2strand(self.from_strand), self.to_id, bin2strand(self.to_strand)]
        return "\t".join([str(x) for x in info])

class layout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Float)
    y = db.Column(db.Float)
    component = db.Column(db.Integer)

    def __init__(self, id, x, y, component):
        self.id = int(id)
        self.x = float(x)
        self.y = float(y)
        self.component = int(component)

    def __repr__(self):
        return str(self.id) + "\t" + str(self.x) + "\t" + str(self.y)


def strand2bin(strand):
    return 1 if strand == "+" else 0
def bin2strand(strand):
    return "+" if strand == 1 else "-"

def drop(app, tablename):

    with app.app_context():

        connection = db.engine.connect()

        # Define the table to be dropped
        metadata = db.MetaData(bind=db.engine)
        your_table = db.Table(tablename, metadata, autoload=True)

        # Drop the table
        your_table.drop(connection)
        connection.close()


def print_tables(app):
    
    with app.app_context():

        rows = gfa_link.query.limit(5).all()
        row_count = gfa_link.query.count()
        print("gfa_link\t", row_count)
        print("--------")
        for row in rows:
            print(row)
        print("--------")

        rows = gfa_segment.query.limit(5).all()
        row_count = gfa_segment.query.count()
        print("gfa_segment\t", row_count)
        print("--------")
        for row in rows:
            print(row)
        print("--------")

        rows = layout.query.limit(5).all()
        row_count = layout.query.count()
        print("layout\t", row_count)
        print("--------")
        for row in rows:
            print(row)
        print("--------")

        rows = chain.query.limit(5).all()
        row_count = chain.query.count()
        print("chain\t", row_count)
        print("--------")
        for row in rows:
            print(row)
        print("--------")

        rows = bubble.query.limit(5).all()
        row_count = bubble.query.count()
        print("bubble\t", row_count)
        print("--------")
        for row in rows:
            print(row)
        print("--------")

        rows = bubble_inside.query.limit(5).all()
        row_count = bubble_inside.query.count()
        print("bubble_inside\t", row_count)
        print("--------")
        for row in rows:
            print(row)
        print("--------")


def add_row_to_gfa_link(line):
    cols = line.split("\t")
    new_row = gfa_link(from_id=cols[1], from_strand=cols[2],
        to_id=cols[3], to_strand=cols[4])
    db.session.add(new_row)
    
def add_row_to_gfa_segment(line):
    cols = line.split("\t")
    new_row = gfa_segment(id=cols[1], seq=cols[2])
    db.session.add(new_row)


def populate_gfa(app, gfa):
    Lcount = 0
    Scount = 0

    with app.app_context():

        with open(gfa) as f:
            for line in f:
                if line[0] == "L":
                    add_row_to_gfa_link(line)
                    Lcount += 1
                    if Lcount % 100000 == 0:
                        sys.stdout.write('L')
                        sys.stdout.flush()
                        db.session.commit()

                if line[0] == "S":
                    add_row_to_gfa_segment(line)
                    Scount += 1
                    if Scount % 100000 == 0:
                        sys.stdout.write('S')
                        sys.stdout.flush()
                        db.session.commit()

        db.session.commit()

def add_row_to_layout(line):
    cols = line.split("\t")
    new_row = layout(id=cols[0], x=cols[1], y=cols[2], component=cols[3])
    db.session.add(new_row)

def populate_tsv(app, tsv):
    count = 0

    with app.app_context():
        skipFirst=True

        with open(tsv) as f:
            for line in f:
                if skipFirst:
                    skipFirst=False
                    continue
                add_row_to_layout(line)
                count += 1
                if count % 100000 == 0:
                    sys.stdout.write('.')
                    sys.stdout.flush()
                    db.session.commit()

class chain(db.Model):
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

class bubble(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chain_id = db.Column(db.Integer)

    type = db.Column(db.String)
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)

    def __init__(self, id, chain_id, type, start, end):
        self.id = int(id)
        self.chain_id = int(chain_id)        
        self.type = type
        self.start = int(start)
        self.end = int(end)
        
    def __repr__(self):
        return str(self.id) + "\t[" + str(self.start) + ", " + str(self.end) + "]"

class bubble_inside(db.Model):
    id = db.Column(db.String, primary_key=True)
    node_id = db.Column(db.Integer, primary_key=True)
    bubble_id = db.Column(db.Integer)

    def __init__(self, id, bubble_id):
        self.id = str(id) + "_" + str(bubble_id)
        self.node_id = int(id)
        self.bubble_id = int(bubble_id)        
        
    def __repr__(self):
        return str(self.id) + " -> " + str(self.bubble_id)


def populate_bubbles(app, jsonFile):
    count = 0

    with app.app_context():
        with open(jsonFile) as f:
            bubbleJson = json.load(f)

            for bubbleId in bubbleJson:
                c = bubbleJson[bubbleId]
                
                sb = None if "parent_sb" not in c else c["parent_sb"]
                pc = None if "parent_chain" not in c else c["parent_chain"]

                new_chain_row = chain(id=c["chain_id"], start=c["ends"][0], end=c["ends"][1],
                    parent_sb=sb, parent_chain=pc)
                db.session.add(new_chain_row)

                for b in c["bubbles"]:
                    new_bubble_row = bubble(id=b["id"], chain_id=c["chain_id"], 
                        type=b["type"], start=b["ends"][0], end=b["ends"][1])
                    db.session.add(new_bubble_row)

                    for inside in b["inside"]:
                        new_bubble_inside_row = bubble_inside(id=inside, bubble_id=b["id"])
                        db.session.add(new_bubble_inside_row)

                count = count+1
                if count % 1000 == 0:
                    sys.stdout.write('B')
                    sys.stdout.flush()
                    db.session.commit()
