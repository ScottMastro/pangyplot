from flask import Flask, render_template, request, make_response, redirect
from cytoband import get_cytoband 
import gfa

app = Flask(__name__)


@app.route('/select', methods=["GET"])
def select():
    chromosome = request.args.get("chromosome")
    start = request.args.get("start")
    end = request.args.get("end")

    #gfa.test(chromosome, start, end)
    
    #temp
    TSV = "static/data/DRB1-3123_sorted.lay.tsv"
    GFA = "static/data/DRB1-3123_sorted.gfa"
    BUBBLE= "static/data/DRB1-3123_sorted.bubble.json"

    print("making graph")

    graph = gfa.add_nodes(TSV)
    graph = gfa.add_links(GFA, graph)

    bubbles = gfa.replace_bubbles(BUBBLE, graph)
    bubbles = gfa.group_bubble(bubbles)


    #graph = gfa.replace_insertion(BUBBLE, graph)
    #graph = gfa.replace_superbubbles(BUBBLE, graph)

    graph = gfa.annotate_graph(bubbles, graph)


    graphNodes = []
    graphLinks = []
    for nodeId in graph:
        
        graphNodes.extend(graph[nodeId].to_node_dict())
        graphLinks.extend(graph[nodeId].to_link_dict())
    
    resultDict = {"nodes": graphNodes, "links": graphLinks}
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
