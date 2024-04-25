import argparse

from db.neo4j_db import db_init
import db.modify.drop_data as drop
from parser.parse_gfa import parse_graph
from parser.parse_layout import parse_layout
from parser.parse_gff3 import parse_gff3
from parser.parse_positions import parse_positions

import db.bubble_gun as bubble_gun
from db.utils.check_status import get_status


def parse_args(app):

    DEFAULT_DB = "default"
    with app.app_context():

        parser = argparse.ArgumentParser(description="PangyPlot command line options.")

        subparsers = parser.add_subparsers(dest='command', help='Available commands', required=True)

        parser_status = subparsers.add_parser('status', help='Check the database status.')

        parser_run = subparsers.add_parser('run', help='Launch the software.')
        parser_run.add_argument('--db', help='Database name', default=DEFAULT_DB, required=True)

        parser_add = subparsers.add_parser('add', help='Add a dataset.')
        parser_add.add_argument('--db', help='Database name', default=DEFAULT_DB, required=True)
        parser_add.add_argument('--ref', help='Reference name', default=None, required=True)
        parser_add.add_argument('--gfa', help='Path to the rGFA file', default=None, required=True)
        parser_add.add_argument('--layout', help='Path to the odgi layout TSV file', default=None, required=True)
        parser_add.add_argument('--positions', help='Path to a position TSV file', default=None, required=False)
        parser_add.add_argument('--compact', help='Attempt to compact graph (not recommended for large graph)', action='store_true', required=False)

        parser_annotate = subparsers.add_parser('annotate', help='Add annotation dataset.')
        parser_annotate.add_argument('--ref', help='Reference name', default=None)
        parser_annotate.add_argument('--gff3', help='Path to the GFF3 file', default=None, required=True)

        parser_drop = subparsers.add_parser('drop', help='Drop data tables')
        parser_drop.add_argument('--db', help='Drop from only one database (provide name).', default=DEFAULT_DB)
        parser_drop.add_argument('--annotations', help='Drop annotations.', action='store_true')
        parser_drop.add_argument('--all', help='Drop everything.', action='store_true')

        parser_example = subparsers.add_parser('example', help='Adds exaple data.')
        parser_example.add_argument('--chrM', help='Use HPRC chrM data', action='store_true')
        parser_example.add_argument('--gencode', help='Add genocode annotations', action='store_true')
        parser.add_argument('--drb1', help='Use DRB1 demo data', action='store_true')

        args = parser.parse_args()

        if args.command == 'status':
            db_init(None)
            get_status()
            exit

        if args.command == 'run':
            db_init(args.db)
            app.run()
            exit

        if args.command == 'drop':
            db_init(args.db)

            flag = False

            if args.all:
                print(f"Dropping everything...")
                drop.drop_all()
                flag = True


            if args.db:
                print(f'Dropping "{args.db}" data...')
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
                args.ref = None
                args.gfa = "static/data/DRB1-3123_sorted.gfa"
                args.layout = "static/data/DRB1-3123_sorted.lay.tsv"
                args.bubbles = "static/data/DRB1-3123_sorted.bubble.json"

            if args.chrM:
                args.command = "add"
                args.db = "chrM"
                args.gfa = "static/data/hprc-v1.0-mc-grch38.chrM.gfa"
                args.ref = "GRCh38"
                args.layout = "static/data/hprc-v1.0-mc-grch38.chrM.lay.tsv"
            
        if args.command == 'annotate':
            print("Adding annotations...")
            db_init(None)
            if args.gff3 and args.ref:
                #drop.drop_annotations()
                print("Parsing GFF3...")
                parse_gff3(args.gff3, args.ref)

        if args.command == "add":
            db_init(args.db)
            
            positions = dict()
            if args.positions:
                print("Parsing positions...")
                positions = parse_positions(args.positions)

            if args.gfa and args.ref and args.layout:

                print("Parsing layout...")
                layoutCoords = parse_layout(args.layout)
                print("Parsing GFA...")
                parse_graph(args.gfa, args.ref, positions, layoutCoords)
                
                #drop.drop_bubbles()
                print("Calculating bubbles...")
                bubble_gun.shoot(args.compact, True)
                print("Done.")
          
