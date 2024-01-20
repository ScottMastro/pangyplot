from flask import Flask, render_template, request, jsonify, make_response
from cytoband import get_cytoband 
from db.neo4j_db import db_init
from db.query.query_top_level import get_top_level
from db.query.query_annotation import get_genes_in_range,text_search_gene
from db.query.query_subgraph import get_subgraph
from db.query.query_all import query_all_chromosomes

import db.modify.drop_data as drop

from parser.parse_gfa import parse_graph
from parser.parse_layout import parse_layout
from parser.parse_gff3 import parse_gff3
import db.bubble_gun as bubble_gun
from db.modify.graph_modify import add_null_nodes, connect_bubble_ends_to_chain, add_chain_subtype

import argparse

app = Flask(__name__)

def create_app():
    db_init()

@app.route('/select', methods=["GET"])
def select():
    genome = request.args.get("genome")
    chrom = genome + "#" + request.args.get("chromosome")
    start = request.args.get("start")
    end = request.args.get("end")
    print(f"Making graph for {chrom}:{start}-{end}...")
    
    start = int(start)
    end = int(end)

    resultDict = get_top_level(chrom, start, end)
    
    return resultDict, 200

@app.route('/genes', methods=["GET"])
def genes():
    genome = request.args.get("genome")
    chrom = genome + "#" + request.args.get("chromosome")
    start = request.args.get("start")
    end = request.args.get("end")
    print(f"Getting genes in {chrom}:{start}-{end}...")
    
    start = int(start)
    end = int(end)
    
    resultDict = {}
    resultDict["genes"] = get_genes_in_range(chrom, start, end)
    resultDict["annotations"] = []

    return resultDict, 200

@app.route('/subgraph', methods=["GET"])
def subgraph():
    nodeid = request.args.get("nodeid")
    genome = request.args.get("genome")
    chrom = genome + "#" + request.args.get("chromosome")
    start = request.args.get("start")
    end = request.args.get("end")

    start = int(start)
    end = int(end)

    print(f"Getting subgraph for {nodeid}...")

    nodeid = int(nodeid)
    resultDict = get_subgraph(nodeid, chrom, start, end)
    return resultDict, 200

@app.route('/chromosomes', methods=["GET"])
def chromosomes():
    genome = request.args.get("genome")

    canonical = [f"chr{n}" for n in range(1, 23)] + ["chrX", "chrY"]
    noncanonicalOnly = request.args.get('noncanonical', 'false').lower() == 'true'
    
    chromosomes = query_all_chromosomes()
    if noncanonicalOnly:
        chromosomes = [chrom for chrom in chromosomes if chrom.split("#")[-1] not in canonical]
    
    # TODO: make real
    with open("./static/annotations/noncanonical.txt") as file:
        for line in file.readlines():
            chromosomes.append(line)
    
    return chromosomes, 200


@app.route('/haplotypes', methods=["GET"])
def haplotypes():

    resultDict={}
    return resultDict, 200

@app.route('/search')
def search():
    type = request.args.get('type')
    query = request.args.get('query')
    
    results = []

    if type == "gene":
        results = text_search_gene(query)
        for gene in results:
            gene["name"] = gene["gene"]

    return jsonify(results)


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
        parser.add_argument('--bubbles', help='Path to the bubblegun JSON file', action="store_true")
        parser.add_argument('--gff3', help='Path to the GFF3 file', default=None)
        parser.add_argument('--ref', help='Reference assembly name', default=None)
        parser.add_argument('--chrM', help='Use HPRC chrM data', action='store_true')
        #parser.add_argument('--ref', help='GAF file with reference coordinates', default=None)
        parser.add_argument('--demo', help='Use DRB1 demo data', action='store_true')
        parser.add_argument('--drop', help='Drop all tables', action='store_true')
        parser.add_argument('--gencode', help='Add genocode annotations', action='store_true')
        args = parser.parse_args()

        flag = False
        for attr, value in vars(args).items():
            if value:
                flag = True

        if args.drop:
            print("dropping all")
            drop.drop_all()
            #drop.drop_bubbles()
            #drop.drop_annotations()

        if args.gencode:
            args.gff3 = "static/data/gencode.v43.basic.annotation.gff3.gz"
            args.ref = "CHM13"

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

            #print("Parsing bubbles...")
            #parse_bubbles(args.bubbles)
            #print("Done.")
        
        if args.gff3 and args.ref:
            drop.drop_annotations()
            print("Parsing GFF3...")
            parse_gff3(args.gff3, args.ref)
            print("Done.")


        if not flag:
            app.run()
        