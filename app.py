from flask import Flask, render_template, request, make_response
from cytoband import get_cytoband 
import graph_helper as helper
from data.db import db
#import data.db as database
import data.neo4j_db as neo4jdb

import data.query_old as query_old
import data.query as query

import argparse

app = Flask(__name__)

def create_app():
    #database.db_init(app)
    neo4jdb.db_init()
@app.route('/select', methods=["GET"])
def select():
    chromosome = request.args.get("chromosome")
    start = request.args.get("start")
    end = request.args.get("end")
    
    print("making graph")

    #todo
    #annotations=[]
    #annotations = query.get_annotation_list(chromosome, start, end)

    graph = dict()
    segmentDict = query.get_segments(chromosome, start, end)
    graph = helper.add_annotations(annotations, segmentDict)

    toLinkDict,fromLinkDict = query_old.get_link_dict(chromosome, start, end)
    bubbleList = query_old.get_bubble_list(chromosome, start, end)
    
    graph = helper.construct_graph(segmentDict, toLinkDict, fromLinkDict, bubbleList)

    paths = query_old.get_haplotypes(fromLinkDict, chromosome, start, end)
    pathDict = helper.process_paths(paths, graph)

    resultDict = graph.to_dictionary(segmentDict)
    resultDict = helper.post_process_graph(graph, resultDict)
    resultDict["annotations"] = [annotation.to_dict() for annotation in annotations]
    resultDict["paths"] = pathDict
    
    print("ready")

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
        parser.add_argument('--gfa', help='Path to the GFA file', default=None)
        parser.add_argument('--layout', help='Path to the odgi layout TSV file', default=None)
        parser.add_argument('--bubbles', help='Path to the bubblegun JSON file', default=None)
        parser.add_argument('--gff3', help='Path to the GFF3 file', default=None)
        parser.add_argument('--chrM', help='Use HPRC chrM data', action='store_true')
        parser.add_argument('--ref', help='GAF file with reference coordinates', default=None)
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
            #database.drop_all()
            neo4jdb.drop_all()

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

        if args.ref:
            import data.ingest as ingest
            ingest.store_ref_coords(args.ref)

        if args.bubbles:
            import data.ingest as ingest
            ingest.store_bubbles(db, args.bubbles)

        if args.gff3:
            import data.ingest as ingest
            ingest.store_annotations(db, args.gff3)

        if not flag:
            app.run()
        