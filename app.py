from flask import Flask, render_template, request, make_response, redirect
from cytoband import get_cytoband 
import gfa
import db

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///graph_data.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/graph'
db.init(app)

#temp
#TSV = "static/data/DRB1-3123_sorted.lay.tsv"
#GFA = "static/data/DRB1-3123_sorted.gfa"
#BUBBLE= "static/data/DRB1-3123_sorted.bubble.json"

TSV = "static/data/chr7-test-pg.lay.tsv"
GFA = "static/data/chr7-test-pg.gfa"
BUBBLE= "static/data/chr7-test-pg.bchains.json"


#db.populate_gfa(app, GFA)
#db.populate_tsv(app, TSV)
#db.populate_bubbles(app, BUBBLE)

db.print_tables(app)

@app.route('/select', methods=["GET"])
def select():
    chromosome = request.args.get("chromosome")
    start = request.args.get("start")
    end = request.args.get("end")

    #gfa.test(chromosome, start, end)
    

    print("making graph")

    graph = gfa.add_nodes(TSV)
    graph = gfa.add_links(GFA, graph)

    bubbles = gfa.make_bubbles(BUBBLE, graph)
    bubbles = gfa.group_bubble(bubbles)

    graph = gfa.annotate_graph(bubbles, graph)

    resultDict = gfa.graph_dictionary(bubbles, graph)

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

app.run()
