import os, argparse
from pangyplot_app import DEFAULT_DB, DEFAULT_PORT, initialize_app

import db.neo4j.neo4j_db as db
import db.modify.drop_data as drop
import db.utils.import_export as import_export
import db.utils.check_status as db_status
import utils.environment_setup as setup

from parser.parse_gfa import parse_graph, parse_paths
from parser.parse_layout import parse_layout
from parser.parse_gff3 import parse_gff3
from parser.parse_positions import parse_positions

import preprocess.bubble_gun as bubble_gun
import db.insert.insert_metadata as metadata
from db.query.query_metadata import query_gfa

script_dir = os.path.dirname(os.path.realpath(__file__))

def parse_args():

    parser = argparse.ArgumentParser(description="PangyPlot command line options.")

    subparsers = parser.add_subparsers(dest='command', help='Available commands', required=True)

    parser_status = subparsers.add_parser('status', help='Check the database status.')

    parser_setup = subparsers.add_parser('setup', help='Setup the environment for database connection.')

    parser_run = subparsers.add_parser('run', help='Launch the software (development mode).')
    parser_run.add_argument('--db', help='Database name', default=DEFAULT_DB)
    parser_run.add_argument('--port', help='Port to run the app on', default=DEFAULT_PORT, type=int, required=False)
    
    parser_run2 = subparsers.add_parser('run2', help='Launch the software (development mode).')
    parser_run2.add_argument('--db', help='Database name', default=DEFAULT_DB)

    parser_add = subparsers.add_parser('add', help='Add a dataset.')
    parser_add.add_argument('--db', help='Database name', default=DEFAULT_DB)
    parser_add.add_argument('--ref', help='Reference name', default=None, required=True)
    parser_add.add_argument('--gfa', help='Path to the GFA file', default=None, required=True)
    parser_add.add_argument('--layout', help='Path to the odgi layout TSV file', default=None, required=True)
    parser_add.add_argument('--positions', help='Path to a position TSV file', default=None, required=True)
    parser_add.add_argument('--update', help='If database name already exists, add to it.', action='store_true')
    parser_add.add_argument('--collection', help='Select collection integer id (not recommended)', default=None, required=False)

    parser_index = subparsers.add_parser('index', help='Index a dataset.')
    parser_index.add_argument('--db', help='Database name', default=DEFAULT_DB)
    parser_index.add_argument('--chr', help='Chromosome name', required=True)
    parser_index.add_argument('--ref', help='Reference name', default=None, required=True)
    parser_index.add_argument('--gfa', help='Path to the GFA file', default=None, required=True)
    parser_index.add_argument('--layout', help='Path to the odgi layout TSV file', default=None, required=True)

    parser_paths = subparsers.add_parser('paths', help='Store all paths from a GFA file.')
    parser_paths.add_argument('--db', help='Database name', default=DEFAULT_DB)
    parser_paths.add_argument('--gfa', help='Path to the GFA file', default=None, required=True)

    parser_annotate = subparsers.add_parser('annotate', help='Add annotation dataset.')
    parser_annotate.add_argument('--ref', help='Reference path name (or substring)', default=None, required=True)
    parser_annotate.add_argument('--gff3', help='Path to the GFF3 file', default=None, required=True)

    parser_drop = subparsers.add_parser('drop', help='Drop data tables')
    parser_drop.add_argument('--db', help='Drop from this database.', default=DEFAULT_DB)
    parser_drop.add_argument('--drop-db', help='Drop the full database.', action='store_true')
    parser_drop.add_argument('--collection', help='Drop from only one collection (provide collection id).', required=False)
    parser_drop.add_argument('--annotations', help='Drop annotations.', action='store_true')
    parser_drop.add_argument('--all', help='Drop all data from neo4j.', action='store_true')

    parser_export = subparsers.add_parser('export', help='Export the processed database directly to a file.')
    parser_export.add_argument('--db', help='Database name', required=True)
    parser_export.add_argument('--collection', help='Export from only one collection (provide collection id).', required=False)
    parser_export.add_argument('--out', help='Output file prefix', required=True)

    parser_import = subparsers.add_parser('import', help='Import a processed database directly from a file (ie. produced by pangyplot export).')
    parser_import.add_argument('--input', help='Input file path', required=True)

    parser_example = subparsers.add_parser('example', help='Adds example DRB1 data.')
    #parser_example.add_argument('--chrM', help='Use HPRC chrM data', action='store_true')
    #parser_example.add_argument('--gencode', help='Add genocode annotations', action='store_true')
    #parser.add_argument('--drb1', help='Use DRB1 demo data', action='store_true')

    args = parser.parse_args()

    if args.command == 'run':
        initialize_app(db_name=args.db, port=args.port)
    elif args.command == 'setup':
        setup.handle_setup_env()
    elif args.command == 'status':
        db_status.get_status()
    elif args.command == 'export':
        import_export.export_database(args.db, args.out, args.collection)
    elif args.command == 'import':
        import_export.import_dataset(args.input)

    elif args.command == 'drop':

        if args.all:
            confirm = input("Are you sure you want to drop EVERYTHING? [y/N]: ")
            if confirm.lower() != 'y':
                print("Aborted.")
                exit()
            print(f"Dropping everything...")
            db.db_init(args.db)
            drop.drop_all()
            exit()

        if args.drop_db:
            confirm = input(f"""Are you sure you want to drop the entire db "{args.db}"? [y/N]: """)
            if confirm.lower() != 'y':
                print("Aborted.")
                exit()
            print(f'Dropping "{args.db}" data...')
            db.db_init(args.db)
            drop.drop_db(args.db)
            exit()

        if args.collection:
            confirm = input(f"""Are you sure you want to drop the entire collection "{args.collection}"? [y/N]: """)
            if confirm.lower() != 'y':
                print("Aborted.")
                exit()
            print(f'Dropping where collection={args.collection} in db {args.db}...')
            db.db_init(args.db)
            drop.drop_collection(args.collection)
            exit()

        if args.annotations:
            confirm = input(f"""Are you sure you want to drop all annotations? [y/N]: """)
            if confirm.lower() != 'y':
                print("Aborted.")
                exit()
            db.db_init(args.db)
            drop.drop_annotations()
            exit()

        print("Nothing dropped. Please specify objects to drop.")
        exit()

    elif args.command == 'annotate':
        print("Adding annotations...")
        db.db_init(None)
        if args.gff3 and args.ref:
            #todo: check if exists, check if should be dropped?
            #drop.drop_annotations()
            print("Parsing GFF3...")
            parse_gff3(args.gff3, args.ref)

    elif args.command == "index":
        datastore_path = os.path.join(script_dir, "datastore")
        datastore_path = os.path.join(datastore_path, args.db)

        if os.path.exists(datastore_path) and False:
            response = input(f"Do you want to add to database '{args.db}'? [y/N]: ").strip().lower()
            if response != 'y':
                print("Aborting.")
                exit(1)
        #else:
        #    os.mkdir(datastore_path)

        chr_path = os.path.join(datastore_path, args.chr)
        if os.path.exists(chr_path):
            response = input(f"Index for '{args.chr}' already exists. Do you want to overwrite it? [y/N]: ").strip().lower()
            if response != 'y':
                print("Aborting.")
                exit(1)
        else:
            os.mkdir(chr_path)
        
        print(f"Indexing GFA file {args.gfa}...")

        import preprocess.bubble.bubble_gun as bubble_gun
        from preprocess.gfa.parse_gfa import parse_gfa
        from preprocess.bubble.construct_bubble_index import construct_bubble_index

        layout_coords = parse_layout(args.layout)
        segment_dict, link_dict  = parse_gfa(args.gfa, args.ref, layout_coords, chr_path)
        bubble_gun_graph = bubble_gun.shoot(segment_dict, link_dict)
        bubble_index = construct_bubble_index(bubble_gun_graph, chr_path)

    if args.command == "run2":
        datastore_path = os.path.join(script_dir, "datastore")
        datastore_path = os.path.join(datastore_path, args.db)
        from preprocess.gfa.data_structures.SegmentIndex import SegmentIndex
        from preprocess.gfa.data_structures.LinkIndex import LinkIndex
        from db.objects.StepIndex import StepIndex
        from preprocess.bubble.BubbleIndex import BubbleIndex
        from pympler.asizeof import asizeof

        segment_index = dict()
        link_index = dict()
        step_index = dict()
        bubble_index = dict()

        for chr in os.listdir(datastore_path):

            print(f"Loading: {chr}")
            chr_dir = os.path.join(datastore_path, chr)

            segment_index[chr] = SegmentIndex(chr_dir)
            print(f"segment_index size:      {asizeof(segment_index[chr]) / 1024**2:.2f} MB")

            link_index[chr] = LinkIndex(chr_dir)
            print(f"link_index size:      {asizeof(link_index[chr]) / 1024**2:.2f} MB")

            step_index[chr] = StepIndex(chr_dir)
            print(f"step_index size:      {asizeof(step_index[chr]) / 1024**2:.2f} MB")

            bubble_index[chr] = BubbleIndex(chr_dir)
            print(f"bubble_index size:      {asizeof(bubble_index[chr]) / 1024**2:.2f} MB")

        print(f"segment_index size total:      {asizeof(segment_index) / 1024**2:.2f} MB")
        print(f"link_index size total:      {asizeof(link_index) / 1024**2:.2f} MB")
        print(f"step_index size total:      {asizeof(step_index) / 1024**2:.2f} MB")
        print(f"bubble_index size total:      {asizeof(bubble_index) / 1024**2:.2f} MB")    

    elif args.command == "add" or args.command == "example":

        if args.command == "example":
            args.command = "add"
            args.db = "example"
            args.ref = "example"
            args.update = False
            args.gfa = "static/data/DRB1-3123_sorted.gfa"
            args.layout = "static/data/DRB1-3123_sorted.lay.tsv"
            args.positions = "static/data/DRB1-3123_sorted.node_positions.txt"

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

        collection_id = metadata.insert_new_collection(args.gfa, args.ref, args.collection)
        if collection_id is None:
            print(f'Failed to create a new collection. Terminating.')
            exit(1)

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
        
    elif args.command == "paths":
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
        
        #debugging: 
        #drop.drop_paths()

        # todo in the future: custom file format that avoids using neo4j
        # https://chatgpt.com/share/6830c502-8d40-800b-bbbf-dc1ccc495171

        print("Parsing GFA...")
        parse_paths(args.gfa)

        print("Done.")


    exit(0)


if __name__ == '__main__':
    parse_args()
