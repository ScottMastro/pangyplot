import argparse

from db.neo4j_db import db_init
import db.modify.drop_data as drop
from parser.parse_gfa import parse_graph
from parser.parse_layout import parse_layout
from parser.parse_gff3 import parse_gff3
import db.bubble_gun as bubble_gun

from db.modify.graph_modify import add_null_nodes, connect_bubble_ends_to_chain, add_chain_subtype

def parse_args(app):

    with app.app_context():

        parser = argparse.ArgumentParser(description="PangyPlot command line options.")

        subparsers = parser.add_subparsers(dest='command', help='Available commands', required=True)

        parser_run = subparsers.add_parser('run', help='Launch the software.')
        
        parser_add = subparsers.add_parser('add', help='Add a dataset.')
        parser_add.add_argument('--db', help='Database name', default=None, required=True)
        parser_add.add_argument('--gfa', help='Path to the rGFA file', default=None, required=True)
        parser_add.add_argument('--layout', help='Path to the odgi layout TSV file', default=None, required=True)
        parser_add.add_argument('--bubbles', help='Path to the bubblegun JSON file', default=None, required=True)

        parser_annotate = subparsers.add_parser('annotate', help='Add annotation dataset.')
        parser_annotate.add_argument('--ref', help='Reference name', default=None)
        parser_annotate.add_argument('--gff3', help='Path to the GFF3 file', default=None, required=True)


        parser_drop = subparsers.add_parser('drop', help='Drop data tables')
        parser_drop.add_argument('--db', help='Drop from only one database (provide name).', default=None)
        parser_drop.add_argument('--annotations', help='Drop annotations.', action='store_true')
        parser_drop.add_argument('--all', help='Drop everything.', action='store_true')

        parser_example = subparsers.add_parser('example', help='Adds exaple data.')
        parser_example.add_argument('--chrM', help='Use HPRC chrM data', action='store_true')
        parser_example.add_argument('--gencode', help='Add genocode annotations', action='store_true')
        parser.add_argument('--drb1', help='Use DRB1 demo data', action='store_true')

        args = parser.parse_args()

        if args.command == 'run':
            db_init(None)
            app.run()
            exit

        if args.command == 'drop':
            db_init(args.db)

            flag = False

            if args.all:
                print(f"Dropping everything...")
                drop.drop_all()
                exit

            if args.db:
                print(f'Dropping "{args.db}" tables...')
                drop.drop_db(args.db)
                flag = True

            if args.annotations:
                drop.drop_annotations()
                flag = True

            if not flag:
                print("Nothing dropped. Please specify objects to drop.")
            exit

        if args.command == "example":
            if args.gencode:
                args.command = "annotate"
                args.gff3 = "static/data/gencode.v43.basic.annotation.gff3.gz"
                args.ref = "CHM13"

            if args.drb1:
                args.command = "add"
                args.db = "DRB1-3123"
                args.gfa = "static/data/DRB1-3123_sorted.gfa"
                args.layout = "static/data/DRB1-3123_sorted.lay.tsv"
                args.bubbles = "static/data/DRB1-3123_sorted.bubble.json"

            if args.chrM:
                args.command = "add"
                args.db = "chrM"
                args.gfa = "static/data/hprc-v1.0-mc-grch38.chrM.gfa"
                args.layout = "static/data/hprc-v1.0-mc-grch38.chrM.lay.tsv"
                args.bubbles = "static/data/hprc-v1.0-mc-grch38.chrM.json"
            
        if args.command == 'annotate':
            print("Adding annotations...")
            db_init(None)
            if args.gff3 and args.ref:
                drop.drop_annotations()
                print("Parsing GFF3...")
                parse_gff3(args.gff3, args.ref)
                print("Done.")

        if args.command == "add":
            if (args.gfa and args.layout is None) or (args.gfa is None and args.layout) :
                print("Both GFA and layout TSV file required to construst graph!")
                parser.print_help()

            if (args.gff3 and args.ref is None):
                print("Need specify --ref when parsing GFF3 file!")
                parser.print_help()

            if args.gfa and args.layout:
                print("Parsing layout...")
                layoutCoords = parse_layout(args.layout)
                print("Parsing GFA...")
                parse_graph(args.gfa, layoutCoords)
                
            if args.bubbles:
                #drop.drop_bubbles()
                print("Calculating bubbles...")
                bubble_gun.shoot()
                add_null_nodes()
                connect_bubble_ends_to_chain()
                add_chain_subtype()
                print("Done.")
          
