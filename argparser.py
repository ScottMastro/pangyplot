import argparse, uuid

import db.neo4j_db as db
import db.modify.drop_data as drop

import environment_setup as setup

from parser.parse_gfa import parse_graph
from parser.parse_layout import parse_layout
from parser.parse_gff3 import parse_gff3
from parser.parse_positions import parse_positions

import preprocess.bubble_gun as bubble_gun
from db.utils.check_status import get_status
import db.insert.insert_metadata as metadata

def parse_args(app):

    DEFAULT_DB = "default"
    DEFAULT_PORT = 5700

    with app.app_context():

        parser = argparse.ArgumentParser(description="PangyPlot command line options.")

        subparsers = parser.add_subparsers(dest='command', help='Available commands', required=True)

        parser_status = subparsers.add_parser('status', help='Check the database status.')

        parser_setup = subparsers.add_parser('setup', help='Setup the environment for database connection.')

        parser_run = subparsers.add_parser('run', help='Launch the software.')
        parser_run.add_argument('--db', help='Database name', default=DEFAULT_DB)
        parser_run.add_argument('--port', help='Port to run the app on', default=DEFAULT_PORT, type=int, required=False)
        
        parser_add = subparsers.add_parser('add', help='Add a dataset.')
        parser_add.add_argument('--db', help='Database name', default=DEFAULT_DB)
        parser_add.add_argument('--ref', help='Reference name', default=None, required=True)
        parser_add.add_argument('--gfa', help='Path to the rGFA file', default=None, required=True)
        parser_add.add_argument('--layout', help='Path to the odgi layout TSV file', default=None, required=True)
        parser_add.add_argument('--positions', help='Path to a position TSV file', default=None, required=True)
        parser_add.add_argument('--update', help='If database name already exists, add to it.', action='store_true')

        parser_annotate = subparsers.add_parser('annotate', help='Add annotation dataset.')
        parser_annotate.add_argument('--ref', help='Reference name', default=None, required=True)
        parser_annotate.add_argument('--gff3', help='Path to the GFF3 file', default=None, required=True)

        parser_drop = subparsers.add_parser('drop', help='Drop data tables')
        parser_drop.add_argument('--db', help='Drop from this database.', default=DEFAULT_DB)
        parser_drop.add_argument('--drop-db', help='Drop the full database.', action='store_true')
        parser_drop.add_argument('--collection', help='Drop from only one collection (provide collection id).', required=False)
        parser_drop.add_argument('--annotations', help='Drop annotations.', action='store_true')
        parser_drop.add_argument('--all', help='Drop all data from neo4j.', action='store_true')

        #parser_example = subparsers.add_parser('example', help='Adds exaple data.')
        #parser_example.add_argument('--chrM', help='Use HPRC chrM data', action='store_true')
        #parser_example.add_argument('--gencode', help='Add genocode annotations', action='store_true')
        #parser.add_argument('--drb1', help='Use DRB1 demo data', action='store_true')

        args = parser.parse_args()

        if args.command == 'setup':
            setup.handle_setup_env()
            exit()

        if args.command == 'status':
            db.db_init(None)
            get_status()
            exit()

        if args.command == 'run':
            db.db_init(args.db)
            port = args.port if args.port else DEFAULT_PORT
            print(f"Starting PangyPlot... http://127.0.0.1:{port}")
           
            app.run(port=port)
            exit()

        if args.command == 'drop':
            db.db_init(args.db)

            if args.all:
                confirm = input("Are you sure you want to drop EVERYTHING? [y/N]: ")
                if confirm.lower() != 'y':
                    print("Aborted.")
                    exit()
                print(f"Dropping everything...")
                drop.drop_all()
                exit()

            if args.drop_db:
                confirm = input(f"""Are you sure you want to drop the entire db "{args.db}"? [y/N]: """)
                if confirm.lower() != 'y':
                    print("Aborted.")
                    exit()
                print(f'Dropping "{args.db}" data...')
                drop.drop_db(args.db)
                exit()

            if args.collection:
                confirm = input(f"""Are you sure you want to drop the entire collection "{args.collection}"? [y/N]: """)
                if confirm.lower() != 'y':
                    print("Aborted.")
                    exit()
                print(f'Dropping where collection={args.collection} in db {args.db}...')
                drop.drop_collection(args.collection)
                exit()


            if args.annotations:
                confirm = input(f"""Are you sure you want to drop all annotations? [y/N]: """)
                if confirm.lower() != 'y':
                    print("Aborted.")
                    exit()
                drop.drop_annotations()
                exit()

            print("Nothing dropped. Please specify objects to drop.")
            exit()

        #todo (add positions file)
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
            db.db_init(None)
            if args.gff3 and args.ref:
                #todo: check if exists, check if should be dropped?
                #drop.drop_annotations()
                print("Parsing GFF3...")
                parse_gff3(args.gff3, args.ref)

        if args.command == "add":
            exists = db.db_init(args.db)
            
            if exists and not args.update:

                add_response = input(f'Add data to existing database "{args.db}"? [y/n]: ').strip().lower()
                if add_response != 'y':
                    delete_response = input(f'Database "{args.db}" already contains data. Drop and recreate it? [y/n]: ').strip().lower()

                    if delete_response == 'y':
                        print(f'Dropping "{args.db}" data...')
                        drop.drop_db(args.db)
                    else:
                        print("Exiting. No changes made.")
                        exit(0)

            collection_id = metadata.insert_new_collection(args.gfa, args.ref)
            db.initiate_collection(collection_id)

            positions = dict()
            if args.positions:
                print("Parsing positions...")
                positions = parse_positions(args.positions)

            if args.gfa and args.ref and args.layout:

                print("Parsing layout...")
                layoutCoords = parse_layout(args.layout)
                print("Parsing GFA...")
                parse_graph(args.gfa, args.ref, positions, layoutCoords)
                
                #debugging: 
                #drop.drop_bubbles()
                #drop.drop_anchors()
                #drop.drop_subgraphs()

                print("Calculating bubbles...")
                bubble_gun.shoot(True)

                #print("Calculating clusters...")
                #cluster.generate_clusters()

                print("Done.")
          
