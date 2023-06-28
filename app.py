from flask import Flask, render_template, request, make_response
from cytoband import get_cytoband 
import graph_helper as helper
from data.db import db, db_config
import argparse

app = Flask(__name__)

#temp
TSV = "static/data/DRB1-3123_sorted.lay.tsv"
GFA = "static/data/DRB1-3123_sorted.gfa"
BUBBLE= "static/data/DRB1-3123_sorted.bubble.json"
GFF3= "static/data/gencode.v43.basic.annotation.gff3.gz"


TSV = "static/data/hprc-v1.0-mc-grch38.chrM.lay.tsv"
GFA = "static/data/hprc-v1.0-mc-grch38.chrM.gfa"
BUBBLE= "static/data/hprc-v1.0-mc-grch38.chrM.json"
GFF3= "static/data/gencode.v43.basic.annotation.gff3.gz"

def print_tables(app):
    
    with app.app_context():

        rows = link.query.limit(5).all()
        row_count = link.query.count()
        print("link\t", row_count)
        print("--------")
        for row in rows:
            print(row)
        print("--------")

        rows = segment.query.limit(5).all()
        row_count = segment.query.count()
        print("segment\t", row_count)
        print("--------")
        for row in rows:
            print(row)
        print("--------")

        rows = chain.query.limit(5).all()
        row_count = chain.query.count()
        print("chain\t", row_count)
        print("--------")
        for row in rows:
            print(row)
        print("--------")

        rows = bubble.query.limit(5).all()





def create_app():

    app.config["SQLALCHEMY_DATABASE_URI"] = db_config()
    db.init_app(app)
    
    with app.app_context():
        from data.model import annotation, bubble, bubble_inside, chain, link, segment
        db.create_all()

        inspector = db.inspect(db.engine)

        for table_name in inspector.get_table_names():
            print(f"Table: {table_name}")
            for column in inspector.get_columns(table_name):
                print(f"- {column['name']}: {column['type']}")


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

        print(db)
        parser = argparse.ArgumentParser(description="PangyPlot command line options.")
        parser.add_argument('--gfa', help='Path to the GFA file', default=None)
        parser.add_argument('--layout', help='Path to the odgi layout TSV file', default=None)
        parser.add_argument('--json', help='Path to the JSON file', default=None)
        parser.add_argument('--gff3', help='Path to the GFF3 file', default=None)
        args = parser.parse_args()
        
        flag = False

        if (args.gfa and args.layout is None) or (args.gfa is None and args.layout) :
            print("Both GFA and layout TSV file required to construst graph!")
            parser.print_help()
            flag = True

        if args.gfa and args.layout:
            import data.ingest as ingest
            ingest.store_graph(app, db, args.gfa, args.layout)
            flag = True


        if args.json:
            print('JSON content:')
            flag = True

        if args.gff3:
            print('GFF3 content:')
            flag = True

        if not flag:
            app.run()
        