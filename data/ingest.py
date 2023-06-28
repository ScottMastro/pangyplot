from os import link
import sys

from data.model.segment import Segment
from data.model.link import Link
import data.parser.parse_gfa as gfa_parser
import data.parser.parse_layout as layout_parser

def printl(string):
    sys.stdout.write(string)
    sys.stdout.flush()

def clear(app, db, tablename):
    with app.app_context():
        connection = db.engine.connect()
        metadata = db.MetaData(bind=db.engine)
        table = db.Table(tablename, metadata, autoload=True)
        db.session.query(table).delete()
        db.session.commit()
        connection.close()

def add_row_to_segment(db, line, i, position):
    cols = line.strip().split("\t")

    SN=None ; SO=None ; SR=None
    for col in cols:
        if col.startswith("SN:"):
            SN = col.split(":")[-1]
            continue
        if col.startswith("SO:"):
            SO = col.split(":")[-1]
            continue
        if col.startswith("SR:"):
            SR = col.split(":")[-1]
            continue

    new_row = Segment(id=i, nodeid=cols[1], seq=cols[2], chrom=SN, pos=SO)
    db.session.add(new_row)

def populate_gfa(app, db, gfa):
    printl("Parsing GFA")
    count = 0
    segmentId = 0

    with app.app_context():

        with gfa_parser.get_reader(gfa) as file:
            for line in file:
                row = gfa_parser.parse_line(line)
                if row["type"] == "L":
                    link = Link(row)
                    db.session.add(link)

                elif row["type"] == "S":
                    row["nodeid"] = row["id"]
                    row["id"] = segmentId
                    segmentId += 1

                    segment = Segment(row)
                    db.session.add(segment)

                count += 1
                if count % 1000 == 0:
                    printl(".")
                    db.session.commit()
        
        db.session.commit()
        print(" Done.")

def populate_layout(app, db, layout):
    printl("Parsing layout")
    count=0
    prevLine=None

    with app.app_context():

        with layout_parser.get_reader(layout) as file:
            for line in file:
                
                if prevLine is not None:
                    row = layout_parser.parse_lines(prevLine, line, count-1)
                    if row:
                        segment = Segment.query.get_or_404(row["id"])
                        segment.update_layout(row["x1"], row["y1"], row["x2"], row["x2"])

                prevLine = line
                count += 1

                if count % 1000*2 == 0:
                    printl(".")
                    db.session.commit()
                    
        db.session.commit()
        print(" Done.")

def store_graph(app, db, gfa, layout):
    print("Clearing graph tables...")
    clear(app, db, "link")
    clear(app, db, "segment")
    populate_gfa(app, db, gfa)
    populate_layout(app, db, layout)




    with app.app_context():

        rows = Link.query.limit(5).all()
        row_count = Link.query.count()
        print("link\t", row_count)
        print("--------")
        for row in rows:
            print(row)
        print("--------")

        rows = Segment.query.limit(5).all()
        row_count = Segment.query.count()
        print("segment\t", row_count)
        print("--------")
        for row in rows:
            print(row)
        print("--------")
