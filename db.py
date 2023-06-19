from operator import countOf
from pickle import TRUE
from types import TracebackType
from unittest.result import failfast
from flask_sqlalchemy import SQLAlchemy
import sys
import json
import db_queries as query
import gzip

db = SQLAlchemy()

def get_nodes(graph):
    return query.get_nodes(segment, graph)
def get_edges(graph):
    return query.get_edges(link, graph)
def get_bubbles(bubbles, graph):
    return query.get_bubbles(bubble, bubble_inside, bubbles, graph)
def get_annotations(annotations):
    return query.get_annotations(None, annotations)

def init(app):
    db.init_app(app)

    with app.app_context():

        db.create_all()
        inspector = db.inspect(db.engine)

        for table_name in inspector.get_table_names():
            print(f"Table: {table_name}")
            for column in inspector.get_columns(table_name):
                print(f"- {column['name']}: {column['type']}")

## ============================================================
## annotation
## ============================================================

class annotation(db.Model):
    id = db.Column(db.String, primary_key=True)
    chrom = db.Column(db.String)
    start = db.Column(db.Integer)
    end = db.Column(db.Integer)
    source = db.Column(db.String)
    type = db.Column(db.String)
    gene = db.Column(db.String)
    info = db.Column(db.String)

    def __init__(self, id, chrom, start, end, source, type, gene, info):
        self.id = str(id)
        self.chrom = str(chrom)
        self.start = str(start)
        self.end = str(end)
        self.source = str(source)
        self.type = str(type)
        self.gene = str(gene)
        self.info = str(info)

    def __repr__(self):
        return "\t".join([str(x) for x in [self.id, self.type, self.chrom, self.start, self.end]])



## ============================================================
## graph
## ============================================================

class link(db.Model):
    id = db.Column(db.String, primary_key=True)
    from_strand = db.Column(db.Boolean)
    to_strand = db.Column(db.Boolean)
    from_id = db.Column(db.String)
    to_id = db.Column(db.String)
    #overlap = db.Column(db.String)

    def __init__(self, from_id, from_strand, to_id, to_strand):
        self.id = str(from_id) + from_strand + str(to_id) + to_strand
        self.from_id = str(from_id)
        self.from_strand = strand2bin(from_strand)
        self.to_id = str(to_id)
        self.to_strand = strand2bin(to_strand)

    def __repr__(self):
        info = [self.from_id, bin2strand(self.from_strand), self.to_id, bin2strand(self.to_strand)]
        return "\t".join([str(x) for x in info])

class segment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nodeid = db.Column(db.String)

    seq = db.Column(db.String)
    x1 = db.Column(db.Float)
    y1 = db.Column(db.Float)
    x2 = db.Column(db.Float)
    y2 = db.Column(db.Float)
    chrom = db.Column(db.String)
    pos = db.Column(db.Integer)

    component = db.Column(db.Integer)

    def __init__(self, id, nodeid, seq, chrom, pos):
        self.id = id
        self.nodeid = str(nodeid)
        self.seq = seq
        self.chrom = chrom
        self.pos = pos

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

## ============================================================
## bubbles
## ============================================================

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

class bubble_inside(db.Model):
    id = db.Column(db.String, primary_key=True)
    node_id = db.Column(db.String)
    bubble_id = db.Column(db.Integer)

    def __init__(self, id, bubble_id):
        self.id = str(id) + "_" + str(bubble_id)
        self.node_id = str(id)
        self.bubble_id = int(bubble_id)        
        
    def __repr__(self):
        return str(self.id) + " -> " + str(self.bubble_id)

## ============================================================
## helpers
## ============================================================

def drop(app, tablename):

    with app.app_context():

        connection = db.engine.connect()
        metadata = db.MetaData(bind=db.engine)
        your_table = db.Table(tablename, metadata, autoload=True)
        your_table.drop(connection)
        db.session.commit()
        connection.close()

def clear(app, tablename):

    with app.app_context():

        connection = db.engine.connect()
        metadata = db.MetaData(bind=db.engine)
        your_table = db.Table(tablename, metadata, autoload=True)
        db.session.query(your_table).delete()
        db.session.commit()
        connection.close()


def drop_all(app):
    drop(app, "link")
    drop(app, "segment")
    drop(app, "bubble")
    drop(app, "chain")
    drop(app, "bubble_inside")
def clear_all(app):
    clear(app, "link")
    clear(app, "segment")
    clear(app, "bubble")
    clear(app, "chain")
    clear(app, "bubble_inside")


def print_tables(app):
    
    with app.app_context():

        rows = link.query.limit(5).all()
        row_count = link.query.count()
        print("link\t", row_count)
        print("--------")
        for row in rows:
            print(row)
        print("--------")

        rows = segment.query.limit(5).all()
        row_count = segment.query.count()
        print("segment\t", row_count)
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

## ============================================================
## Annotations populate
## ============================================================

def add_row_to_annotations(line):
    cols = line.strip().split("\t")
    infoCols = cols[8].split(";")
    print(infoCols)
    id = None ; gene = None ; exon = None

    for c in infoCols:
        if c.startswith("ID"):
            id = c.split("=")[1]
        if c.startswith("gene"):
            gene = c.split("=")[1]
        if c.startswith("exon_number"):
            exon = c.split("=")[1]

    print(exon, id)
    new_row = annotation(id=id, chrom=cols[0], start=cols[3], end=cols[4],
                             source=cols[1], type=cols[2], gene=gene, info=cols[8])
    db.session.add(new_row)



def populate_annotations(app, gff3):
    count = 0

    def do_line(line, count):
        if line.startswith("#"):
            return count
    
        add_row_to_annotations(line)
        count += 1
        if count % 1000 == 0:
            sys.stdout.write('L')
            sys.stdout.flush()
            db.session.commit()
        return count

    with app.app_context():

        if gff3.endswith(".gz"):
            with gzip.open(gff3, 'rt') as f:
                for line in f:
                    count = do_line(line, count)
        else:
            with open(gff3) as f:
                for line in f:
                    count = do_line(line, count)

        db.session.commit()

## ============================================================
## GFA populate
## ============================================================

def strand2bin(strand):
    return 1 if strand == "+" else 0
def bin2strand(strand):
    return "+" if strand == 1 else "-"

def add_row_to_segment(line, i, position):
    cols = line.split("\t")
    new_row = segment(id=i, nodeid=cols[1], seq=cols[2], chrom="chr1", pos=position)
    db.session.add(new_row)

def add_row_to_link(line):
    cols = line.split("\t")
    new_row = link(from_id=cols[1], from_strand=cols[2],
        to_id=cols[3], to_strand=cols[4])
    db.session.add(new_row)

def populate_gfa(app, gfa):
    Lcount = 0
    Scount = 0
    position = 0
    
    with app.app_context():

        with open(gfa) as f:
            for line in f:
                if line[0] == "L":
                    add_row_to_link(line)
                    Lcount += 1
                    if Lcount % 100000 == 0:
                        sys.stdout.write('L')
                        sys.stdout.flush()
                        db.session.commit()

                if line[0] == "S":
                    Scount += 1
                    cols = line.split("\t")
                    
                    add_row_to_segment(line, Scount, position)
                    position += len(cols[2])
                    if Scount % 100000 == 0:
                        sys.stdout.write('S')
                        sys.stdout.flush()
                        db.session.commit()

        db.session.commit()

## ============================================================
## odgi layout populate
## ============================================================


def update_row_with_layout(line1, line2):
    cols1 = line1.split("\t")
    cols2 = line2.split("\t")
    id = int(int(cols1[0])/2 + 1)
    id = str(id)
    row = segment.query.get_or_404(id)
    row.update_layout(x1=cols1[1], y1=cols1[2], x2=cols2[1], y2=cols2[2])


def populate_tsv(app, tsv):
    count = 0
    
    skipFirst=True
    prevLine=None
    lineNumber=0
    with app.app_context():

        with open(tsv) as f:
            for line in f:
                if skipFirst:
                    skipFirst=False
                    continue

                lineNumber += 1
                if lineNumber % 2 == 0:
                    update_row_with_layout(prevLine, line)
                    count += 1
                    if count % 100000 == 0:
                        sys.stdout.write('.')
                        sys.stdout.flush()
                prevLine = line


## ============================================================
## bubble json populate
## ============================================================

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
        db.session.commit()


