from math import floor
#import gfapy
import subprocess
import pandas as pd
import json

from cytoband import X

GFATOOLS="/home/scott/bin/gfatools/gfatools"
ODGI="/home/scott/bin/odgi/bin/odgi"
#GFA="./static/data/chr18.smooth.final.gfa"
#TSV="./static/data/chr18.smooth.final.tsv"

TSV = "static/data/DRB1-3123_sorted.lay.tsv"
GFA = "static/data/DRB1-3123_sorted.gfa"
BUBBLE= "static/data/DRB1-3123_sorted.bubble.json"

OG="./static/data/chr6.pan.fa.a2fb268.4030258.b5c839f.smooth.gfa.og"

COLLAPSE_SIMPLE = True

def bubble_dict(file):

    with open(file) as f:
        bubbles = json.load(f)
        return bubbles

def layout_dict(file, skipFirst=True):

    layout = dict()
    with open(file) as t:
        for line in t:
            if skipFirst:
                skipFirst=False
            else:
                # idx,X,Y,component
                cols = line.strip().split("\t")
                idx = int(cols[0])
                xpos = float(cols[1])*10
                ypos = float(cols[2])*5

                nodeId =  floor(idx/2)+1
                
                if nodeId not in layout:
                    node = {"x1": xpos, "y1": ypos}
                    layout[nodeId] = node
                else:
                    layout[nodeId]["x2"] = xpos
                    layout[nodeId]["y2"] = ypos

    return layout

def graph_dict(file):
    graph = dict()

    #todo: flip direction for "negative" strand ex 2078

    with open(file) as f:
        for line in f:
            cols = line.split("\t")
            if cols[0] == "L":
                n1 = int(cols[1]) ; n2 = int(cols[3])

                if n1 not in graph:
                    graph[n1] = {"to": [], "from": []}
                if n2 not in graph:
                    graph[n2] = {"to": [], "from": []}

                graph[n1]["to"].append(n2)
                graph[n2]["from"].append(n1)
    
    return(graph)


def get_id(nodeId, side=1):
    return int(nodeId)*2 + side-1
def get_node(id):
    return floor(id/2)


def distance(node):
    return ((node["x2"] - node["x1"])**2 + (node["y2"] - node["y1"])**2)**0.5


def node_to_bubble_dict(bubbles):
    nodeToBubble = dict()
    
    for superBubbleId in bubbles:     
        for bubble in bubbles[superBubbleId]["bubbles"]:
            bid = int(bubble["id"])
            if bubble["type"] == "simple":
                for nodeId in bubble["inside"]:
                    nid = int(nodeId)
                    if nid not in nodeToBubble:
                        nodeToBubble[nid] = []
                    nodeToBubble[nid].append(bid)
    return nodeToBubble

def init_bubble_graphs(nodeToBubble):
    bubbleGraph = dict()
    for nodeId in nodeToBubble:
        for bubbleId in nodeToBubble[nodeId]:
            if bubbleId not in bubbleGraph:
                bubbleGraph[bubbleId] = {"nodes": [], "links": []}
    return bubbleGraph

def create_nodes(layout, bubbles):
    
    nodes = []
    nodeLinks = []

    nodeToBubble = node_to_bubble_dict(bubbles)
    bubbleGraph = init_bubble_graphs(nodeToBubble)

    for nodeId in layout:
        e = layout[nodeId]
        id1 = get_id(nodeId,1)
        id2 = get_id(nodeId,2)

        n1 = {"nodeid": nodeId, "id": id1, "x": e["x1"], "y": e["y1"], "group": 3, "description": "desc", "size": 3}
        n2 = {"nodeid": nodeId, "id": id2, "x": e["x2"], "y": e["y2"], "group": 3, "description": "desc", "size": 3}
        link = {"source": id1, "target": id2, "group": 3, "width": 10, "length":distance(e), "type": "node"}

        if COLLAPSE_SIMPLE and nodeId in nodeToBubble:

            for bid in nodeToBubble[nodeId]:
                bubbleGraph[bid]["nodes"].extend([n1,n2])
                bubbleGraph[bid]["links"].append(link)
        else:
            nodes.append(n1)
            nodes.append(n2)
            nodeLinks.append(link)

    return nodes, nodeLinks, bubbleGraph

def create_links(graph, bubbles, bubbleGraph):

    nodeToBubble = node_to_bubble_dict(bubbles)
    
    links = []
    for nodeId in graph:
        for nodeIdTo in graph[nodeId]["to"]:

            link = {"source": get_id(nodeId, 2), "target": get_id(nodeIdTo, 1),
                        "group": 2, "width": 1, "length": 30, "type": "edge"}

            if COLLAPSE_SIMPLE and nodeIdTo in nodeToBubble:
                for bid in nodeToBubble[nodeIdTo]:
                    bubbleGraph[bid]["links"].append(link)
            elif COLLAPSE_SIMPLE and nodeId in nodeToBubble:
                for bid in nodeToBubble[nodeId]:
                    bubbleGraph[bid]["links"].append(link)

            else:
                links.append(link)
    
    return links, bubbleGraph


def replace_bubbles(bubbles, bubbleGraph):

    nodeToBubble = node_to_bubble_dict(bubbles)

    bubbleNodes=[]
    bubbleLinks=[]

    for bid in bubbleGraph:
        bgraph = bubbleGraph[bid]
        if len(bgraph["nodes"]) == 0: continue
        
        bstring = "b"+str(bid)
        
        xpos = sum([n["x"] for n in bgraph["nodes"]])/len(bgraph["nodes"])
        ypos = sum([n["y"] for n in bgraph["nodes"]])/len(bgraph["nodes"])

        bnode = {"nodeid": "snp", "id": bstring, "x": xpos, "y": ypos, "group": 12, "description": "desc", "size": 15}
        bubbleNodes.append(bnode)

        links = bubbleGraph[bid]["links"]
        for link in links:
            sourceNodeId = get_node(link["source"])
            targetNodeId = get_node(link["target"])

            if sourceNodeId not in nodeToBubble:
                blink =  {"source": link["source"], "target": bstring,
                        "group": 5, "width": 3, "length": 30, "type": "edge"}
                bubbleLinks.append(blink)
            if targetNodeId not in nodeToBubble:
                blink =  {"source": bstring, "target": link["target"],
                        "group": 6, "width": 3, "length": 30, "type": "edge"}
                bubbleLinks.append(blink)

    return bubbleNodes, bubbleLinks
























# https://odgi.readthedocs.io/en/latest/rst/tutorials/navigating_and_annotating_graphs.html
def odgi_extract(og, region, out):
    print("extracting")

    temp = "og" + "temp.extract"
    params = ["-t", "28", "-P", "-c", "0", "-E", "-d", "0"]
    #subprocess.run([ODGI, "extract", "-i", og, "-r", region, "-o", temp] + params)

    print("sorting")

    subprocess.run([ODGI, "sort", "-i", temp, "-o", out, "-O"])

    print("done")

# https://odgi.readthedocs.io/en/latest/rst/tutorials/sort_layout.html
# odgi layout -i DRB1-3123_unsorted.og -o DRB1-3123_unsorted.og.lay  -T DRB1-3123_unsorted.og.tsv
def odgi_layout(og):

    print("laying out")
    params = ["-P", "--threads", "2"]
    #subprocess.run([ODGI, "layout", "-i", og, "-o", og+".lay", "-T", og+".lay.tsv" ] + params)

    print("done")
    return og+".lay.tsv"

def test(chr, start, end):
    region = chr + "-" + str(start) + ":" + str(end)

    #result = subprocess.run([GFATOOLS, "view", GFA, "-R", region], capture_output=True, text=True).stdout.strip("\n")
    
    region = "grch38#chr6:29000000-34000000"
    extract = "./static/data/chr6.pan.fa.a2fb268.4030258.b5c839f.smooth.gfa.extract.og"
    odgi_extract(OG, region, extract)

    tsv = odgi_layout(extract)

    
    #gfa = gfapy.Gfa.from_file(GFA)
    #print(len(gfa.lines))
    #b = gfa.line("4")
    #b.disconnect()
    #print(gfa.segment_names)
    #for line in gfa.lines: 
    #    print(line[1])






def poke_bubbles(nodes, links, bubbles):
    ends = set()
    colour = dict()
    for i in bubbles:
        bubble = bubbles[i]
        
        # simple, insertion, super
        for b in bubble["bubbles"]:
            if b["type"] == "super":
                for x in b["inside"]:
                    ends.add(int(x))
                    colour[int(x)] = int(i)
            if b["type"] == "simple":
                for x in b["inside"]:
                    ends.add(int(x))
                    colour[int(x)] = 0
    



    for node in nodes:
        #print(node["nodeid"], node["nodeid"] in ends)


        if node["nodeid"] in ends:
            node["group"] = colour[node["nodeid"]]

            #print(node["nodeid"])

    for link in links:

        if link["type"] == "node":
            n1 = nodes[link["source"]]["nodeid"]
            n2 = nodes[link["target"]]["nodeid"]

            if n1 in colour and n2 in colour and colour[n1] == colour[n2]:
                link["group"] = colour[n1]


    return nodes