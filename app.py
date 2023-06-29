from flask import Flask, render_template, request, make_response
from cytoband import get_cytoband 
import graph_helper as helper
from data.db import db
import data.db as database
import data.query as query

import argparse

app = Flask(__name__)

def create_app():
    database.db_init(app)

@app.route('/select', methods=["GET"])
def select():
    chromosome = request.args.get("chromosome")
    start = request.args.get("start")
    end = request.args.get("end")
    
    print("making graph")

    graph = dict()
    graph = query.get_nodes(graph)
    graph = query.get_edges(graph)

    annotations = []
    annotations = query.get_annotations(annotations, chromosome, start, end)
    graph = helper.add_annotations(annotations, graph)

    bubbles = dict()
    bubbles = query.get_bubbles(bubbles, graph)
    bubbles = helper.group_bubbles(bubbles)

    resultDict = helper.get_graph_dictionary(graph, bubbles, annotations)

    print("done")

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
        parser.add_argument('--gfa', help='Path to the GFA file', default=None)
        parser.add_argument('--layout', help='Path to the odgi layout TSV file', default=None)
        parser.add_argument('--bubbles', help='Path to the bubblegun JSON file', default=None)
        parser.add_argument('--gff3', help='Path to the GFF3 file', default=None)
        parser.add_argument('--chrM', help='Use HPRC chrM data', action='store_true')
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
            database.drop_all()

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
            import data.ingest as ingest
            ingest.store_graph(db, args.gfa, args.layout)

        if args.bubbles:
            import data.ingest as ingest
            ingest.store_bubbles(db, args.bubbles)

        if args.gff3:
            import data.ingest as ingest
            ingest.store_annotations(db, args.gff3)

        if not flag:
            app.run()
        