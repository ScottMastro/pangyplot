from flask import Flask, render_template, request, make_response
from cytoband import get_cytoband 
import db.neo4j_db as neo4jdb
import db.query as query
from db.parser.parse_gfa import parse_graph
from db.parser.parse_layout import parse_layout
from db.parser.parse_gff3 import parse_gff3
from db.parser.parse_bubbles import parse_bubbles

import argparse

app = Flask(__name__)

def create_app():
    neo4jdb.db_init()
@app.route('/select', methods=["GET"])
def select():
    chrom = request.args.get("chromosome")
    start = request.args.get("start")
    end = request.args.get("end")
    print(f"Making graph for {chrom}:{start}-{end}...")
    
    start = int(start)
    end = int(end)

    resultDict = query.get_segments(chrom, start, end)
    
    chr = chrom.split("#")[1]
    annotations = query.get_annotations(chr, start, end)
    resultDict["annotations"] = annotations

    print("ready")
    return resultDict, 200

@app.route('/subgraph', methods=["GET"])
def subgraph():
    nodeid = request.args.get("nodeid")
    print(f"Getting subgraph for {nodeid}...")

    nodeid = int(nodeid)
    resultDict = query.get_subgraph(nodeid)
    return resultDict, 200

@app.route('/haplotypes', methods=["GET"])
def haplotypes():

    resultDict={}
    return resultDict, 200


@app.route('/cytoband', methods=["GET"])
def cytobands():
    chromosome = request.args.get("chromosome")
    include_order = request.args.get("include_order")

    resultDict = get_cytoband(chromosome, include_order)
    return resultDict, 200

@app.route('/')
def index():
    content = dict()
    response = make_response(render_template("index.html", **content ))
    return response

if __name__ == '__main__':

    create_app()

    with app.app_context():

        parser = argparse.ArgumentParser(description="PangyPlot command line options.")
        parser.add_argument('--gfa', help='Path to the rGFA file', default=None)
        parser.add_argument('--layout', help='Path to the odgi layout TSV file', default=None)
        parser.add_argument('--bubbles', help='Path to the bubblegun JSON file', default=None)
        parser.add_argument('--gff3', help='Path to the GFF3 file', default=None)
        parser.add_argument('--chrM', help='Use HPRC chrM data', action='store_true')
        #parser.add_argument('--ref', help='GAF file with reference coordinates', default=None)
        parser.add_argument('--demo', help='Use DRB1 demo data', action='store_true')
        parser.add_argument('--drop', help='Drop all tables', action='store_true')
        parser.add_argument('--gencode', help='Add genocode annotations', action='store_true')
        args = parser.parse_args()

        neo4jdb.add_chain_complexity()
        flag = False
        for attr, value in vars(args).items():
            if value:
                flag = True

        if args.drop:
            print("dropping all")
            neo4jdb.drop_all()
            #neo4jdb.drop_bubbles()
            #neo4jdb.drop_annotations()

        if args.gencode:
            args.gff3 = "static/data/gencode.v43.basic.annotation.gff3.gz"

        if args.demo:
            args.gfa = "static/data/DRB1-3123_sorted.gfa"
            args.layout = "static/data/DRB1-3123_sorted.lay.tsv"
            args.bubbles = "static/data/DRB1-3123_sorted.bubble.json"

        if args.chrM:
            args.gfa = "static/data/hprc-v1.0-mc-grch38.chrM.gfa"
            args.layout = "static/data/hprc-v1.0-mc-grch38.chrM.lay.tsv"
            args.bubbles = "static/data/hprc-v1.0-mc-grch38.chrM.json"
            flag = False

        if (args.gfa and args.layout is None) or (args.gfa is None and args.layout) :
            print("Both GFA and layout TSV file required to construst graph!")
            parser.print_help()

        if args.gfa and args.layout:
            print("Parsing layout...")
            layoutCoords = parse_layout(args.layout)
            print("Parsing GFA...")
            parse_graph(args.gfa, layoutCoords)
            print("Done.")
            
        #if args.ref:
            #if ref.endswith(".gaf") or ref.endswith(".gaf.gz"):
            #    parse_coords(ref)

        if args.bubbles:
            print("Parsing bubbles...")
            parse_bubbles(args.bubbles)
            print("Done.")
            
        if args.gff3:
            print("Parsing GFF3...")
            parse_gff3(args.gff3)
            print("Done.")


        if not flag:
            app.run()
        