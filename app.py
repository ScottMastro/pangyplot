from flask import Flask, render_template, request, make_response
from cytoband import get_cytoband 
import graph_helper as helper
from data.db import db, db_init
import argparse

app = Flask(__name__)

def create_app():
    db_init(app)

@app.route('/select', methods=["GET"])
def select():
    chromosome = request.args.get("chromosome")
    start = request.args.get("start")
    end = request.args.get("end")

    #gfa.test(chromosome, start, end)
    
    print("making graph")

    graph = dict()
    graph = data.get_nodes(graph)
    graph = data.get_edges(graph)

    annotations = []
    annotations = data.get_annotations(annotations, chromosome, start, end)
    graph = helper.add_annotations(annotations, graph)

    bubbles = dict()
    bubbles = data.get_bubbles(bubbles, graph)
    bubbles = helper.group_bubbles(bubbles)

    graph = helper.label_group(bubbles, graph)

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
        parser.add_argument('--chr', help='Use HPRC chr data', default=None)
        args = parser.parse_args()
        
        flag = False

        #TSV = "static/data/DRB1-3123_sorted.lay.tsv"
        #GFA = "static/data/DRB1-3123_sorted.gfa"
        #BUBBLE= "static/data/DRB1-3123_sorted.bubble.json"
        #GFF3= "static/data/gencode.v43.basic.annotation.gff3.gz"

        if args.chr:
            args.gfa = "static/data/hprc-v1.0-mc-grch38.chrM.gfa"
            args.layout = "static/data/hprc-v1.0-mc-grch38.chrM.lay.tsv"
            args.bubbles = "static/data/hprc-v1.0-mc-grch38.chrM.json"
            #args.gff3 = "static/data/gencode.v43.basic.annotation.gff3.gz"

        if (args.gfa and args.layout is None) or (args.gfa is None and args.layout) :
            print("Both GFA and layout TSV file required to construst graph!")
            parser.print_help()
            flag = True

        if args.gfa and args.layout:
            import data.ingest as ingest
            ingest.store_graph(db, args.gfa, args.layout)
            flag = True

        if args.bubbles:
            import data.ingest as ingest
            ingest.store_bubbles(db, args.bubbles)
            flag = True

        if args.gff3:
            import data.ingest as ingest
            ingest.store_annotations(db, args.gff3)
            flag = True

        if not flag:
            app.run()
        