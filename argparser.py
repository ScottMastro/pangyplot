import argparse, uuid

import db.neo4j_db as db
import db.modify.drop_data as drop

import environment_setup as setup

from parser.parse_gfa import parse_graph, parse_paths
from parser.parse_layout import parse_layout
from parser.parse_gff3 import parse_gff3
from parser.parse_positions import parse_positions

import preprocess.bubble_gun as bubble_gun
from db.utils.check_status import get_status
import db.insert.insert_metadata as metadata
from db.query.query_metadata import query_gfa

from db.modify.preprocess_modifications import chain_intermediate_segments

import cytoband

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
        
        parser_run.add_argument('--organism', type=str, choices=[
                'none', 'human', 'mouse', 'fruitfly', 'zebrafish', 'chicken', 'rabbit','dog'
            ], default='human', help='Organism for predefined cytoband file (default: human)')

        parser_run.add_argument('--cytoband', type=str, help='Path to custom cytoband file.')
        parser_run.add_argument('--canonical', type=str, help='Path to custom canonical chromosome file.')

        parser_add = subparsers.add_parser('add', help='Add a dataset.')
        parser_add.add_argument('--db', help='Database name', default=DEFAULT_DB)
        parser_add.add_argument('--ref', help='Reference name', default=None, required=True)
        parser_add.add_argument('--gfa', help='Path to the GFA file', default=None, required=True)
        parser_add.add_argument('--layout', help='Path to the odgi layout TSV file', default=None, required=True)
        parser_add.add_argument('--positions', help='Path to a position TSV file', default=None, required=True)
        parser_add.add_argument('--update', help='If database name already exists, add to it.', action='store_true')

        parser_paths = subparsers.add_parser('paths', help='Store all paths from a GFA file.')
        parser_paths.add_argument('--db', help='Database name', default=DEFAULT_DB)
        parser_paths.add_argument('--gfa', help='Path to the GFA file', default=None, required=True)

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

        if args.command == 'cytoband':
            setup.handle_setup_env()
            exit()

        if args.command == 'run':

            if (args.cytoband and not args.canonical) or (args.canonical and not args.cytoband):
                parser.error("Both --cytoband and --canonical must be provided together if using a custom cytoband file.")
                exit(0)

            cytoband.set_cytoband(args.organism, args.cytoband, args.canonical)

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

                add_response = input(f'Database "{args.db}" already contains data. Add data to existing database? [y/n]: ').strip().lower()
                if add_response != 'y':
                    delete_response = input(f'Drop and recreate {args.db}? [y/n]: ').strip().lower()

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
                bubble_gun.shoot()

                print("Done.")
          
    if args.command == "paths":
        exists = db.db_init(args.db)

        if not exists:
            print(f'Database "{args.db}" does not exist. Use "pangyplot add" to first add GFA data.')
            exit(0)

        collections = query_gfa(args.gfa)
        collection_id = None

        if len(collections) == 0:
            print(f'No data found for "{args.gfa}". Use "pangyplot add" to store the GFA first.')
            exit(0)

        elif len(collections) > 1:
            print("Found multiple matching GFA files:")
            for idx, col in enumerate(collections):
                dt = col['datetime']
                print(f"[{idx}] File: {col['file']} | Genome: {col['genome']} | Date: {dt.year}-{dt.month:02}-{dt.day:02} {dt.hour:02}:{dt.minute:02} | ID: {col['id']}")
            
            selection = input("Select the matching GFA file (enter index): ")
            try:
                selected_index = int(selection)
                if selected_index < 0 or selected_index >= len(collections):
                    raise ValueError
                collection_id = collections[selected_index]['id']
            except ValueError:
                print("Invalid selection. Aborting.")
                exit(1)
        else:
            collection_id = collections[0]['id']
        
        db.initiate_collection(collection_id)

        # todo in the future: custom file format that avoids using neo4j
        # https://chatgpt.com/share/6830c502-8d40-800b-bbbf-dc1ccc495171

        print("Parsing GFA...")
        parse_paths(args.gfa)

        print("Done.")
