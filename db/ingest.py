from db.parser.parse_gfa import parse_graph
from db.parser.parse_gaf import parse_coords
from db.parser.parse_layout import parse_layout
from db.parser.parse_gff3 import parse_gff3
from db.parser.parse_bubbles import parse_bubbles


def store_graph(gfa, layout):
    print("Parsing layout...")
    layoutCoords = parse_layout(layout)
    print("Parsing GFA...")
    parse_graph(gfa, layoutCoords)
    print("Done.")

def store_ref_coords(ref):
    if ref.endswith(".gaf") or ref.endswith(".gaf.gz"):
        parse_coords(ref)

def store_annotations(db, gff3):
    print("Parsing GFF3...")
    parse_gff3(gff3)
    print("Done.")

def store_bubbles(bubbles):
    print("Clearing bubbles tables.")
    print("Parsing bubbles...")
    parse_bubbles(bubbles)
    print("Done.")