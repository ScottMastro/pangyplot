import sys
from functools import partial

from data.parser.parse_gfa import populate_gfa
from data.parser.parse_layout import populate_layout
from data.parser.parse_gff3 import parse_gff3
from data.parser.parse_bubbles import parse_bubbles

def printl(string):
    sys.stdout.write(string)
    sys.stdout.flush()

def clear(db, tablename):
    connection = db.engine.connect()
    metadata = db.MetaData(bind=db.engine)
    table = db.Table(tablename, metadata, autoload=True)
    db.session.query(table).delete()
    db.session.commit()
    connection.close()

def count_update_full(db, val, count):
    if count % val == 0:
        printl(".")
        db.session.commit()

def store_graph(db, gfa, layout):
    print("Clearing graph tables.")
    clear(db, "link")
    clear(db, "segment")

    printl("Parsing GFA")
    count_update = partial(count_update_full, db, 1000)
    populate_gfa(db, gfa,  count_update)
    print(" Done.")

    printl("Parsing layout")
    count_update = partial(count_update_full, db, 1000*2)
    populate_layout(db, layout, count_update)
    print(" Done.")

def store_annotations(db, gff3):
    print("Clearing annotations table.")
    clear(db, "annotation")

    printl("Parsing GFF3")
    count_update = partial(count_update_full, db, 100000)
    parse_gff3(db, gff3, count_update)
    print(" Done.")

def store_bubbles(db, bubbles):
    print("Clearing bubbles tables.")
    clear(db, "bubble")
    clear(db, "bubble_inside")

    printl("Parsing bubbles")
    count_update = partial(count_update_full, db, 100)
    parse_bubbles(db, bubbles, count_update)
    print(" Done.")
