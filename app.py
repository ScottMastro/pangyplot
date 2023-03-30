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

    bubbles = gfa.bubble_dict(BUBBLE)
<<<<<<< HEAD
    nodes = gfa.nodes_dict(TSV)
    nodes = gfa.link_dict(GFA, nodes)

    #nodes, links = gfa.replace_bubbles(nodes, links, bubbles)
=======
    graph = gfa.graph_dict(GFA, TSV)

    graph = gfa.replace_bubbles(graph, bubbles)
>>>>>>> 380553c6934f126345072db2e1ffef5febeefeb9

    #nodes, nodeLinks, bubbleGraph = gfa.create_graph(layout, gfa)
    #links, bubbleGraph = gfa.create_links(gfa, bubbles, bubbleGraph)
    #nodes = gfa.poke_bubbles(nodes, links, bubbles)

    graphNodes = []
    graphLinks = []
<<<<<<< HEAD
    for nodeId in nodes:
        print(nodes[nodeId].to_node_dict())
        graphNodes.extend(nodes[nodeId].to_node_dict())
        graphLinks.extend(nodes[nodeId].to_link_dict())
    
=======
    for nodeId in graph:
        graphNodes.extend(graph[nodeId]["nodes"])
        graphLinks.extend(graph[nodeId]["nodeLinks"])
        graphLinks.extend(graph[nodeId]["toLinks"])

>>>>>>> 380553c6934f126345072db2e1ffef5febeefeb9
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
