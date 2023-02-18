from math import floor
#import gfapy
import subprocess
import json

from cytoband import X

GFATOOLS="/home/scott/bin/gfatools/gfatools"
ODGI="/home/scott/bin/odgi/bin/odgi"

OG="./static/data/chr6.pan.fa.a2fb268.4030258.b5c839f.smooth.gfa.og"

COLLAPSE_SIMPLE = True

def get_id(nodeId, side=0):
    return str((int(nodeId)-1)*2 + side)
def get_node(id):
    return str(floor(int(id)/2)+1)

def bubble_dict(file):

    with open(file) as f:
        bubbles = json.load(f)
        return bubbles

def distance(node1, node2):
    return ((node2["x"] - node1["x"])**2 + (node2["y"] - node1["y"])**2)**0.5

def new_subgraph():
    return {"nodes": [], "nodeLinks": [], "toLinks": [], "fromLinks": [], "subgraph": []}

def graph_dict(gfa, layout, skipFirstLayoutLine=True):

    graph = dict()
    with open(layout) as t:
        for line in t:
            if skipFirstLayoutLine:
                skipFirstLayoutLine=False
            else:
                # idx,X,Y,component
                cols = line.strip().split("\t")
                id = cols[0]
                xpos = float(cols[1])*10
                ypos = float(cols[2])*5

                nodeId =  get_node(id)
                
                node = {"nodeid": nodeId, "id": id, "x": xpos, "y": ypos, "group": 3, "description": "desc", "size": 3}

                if nodeId not in graph:
                    graph[nodeId] = new_subgraph()
                
                graph[nodeId]["nodes"].append(node)

    for nodeId in graph:
        n1,n2= graph[nodeId]["nodes"]
        link = {"source": n1["id"], "target": n2["id"], "group": 3, "width": 10, "length":distance(n1,n2), "type": "node"}
        graph[nodeId]["nodeLinks"].append(link)

    with open(gfa) as f:
        for line in f:
            cols = line.split("\t")
            if cols[0] == "L":
                nodeIdFrom = cols[1] ; nodeIdTo = cols[3]
                link = {"source": get_id(nodeIdFrom, 1), "target": get_id(nodeIdTo, 0),
                            "group": 2, "width": 1, "length": 30, "type": "edge"}

                graph[nodeIdFrom]["toLinks"].append(link)
                graph[nodeIdTo]["fromLinks"].append(link)


    return graph

def combine_subgraphs(subgraphs):
    combined = new_subgraph()
    for x in ["nodes", "nodeLinks", "toLinks", "fromLinks", "subgraph"]:
        for subgraph in subgraphs:
            combined[x].extend(subgraph[x])
    return combined

def graph_center(graph):
    xpos = 0 ; ypos = 0 ; n = 0
    for nodeId in graph:
        xpos += sum([n["x"] for n in graph[nodeId]["nodes"]])
        ypos += sum([n["y"] for n in graph[nodeId]["nodes"]])
        n += len(graph[nodeId]["nodes"])
    return (xpos/n, ypos/n)

def generate_bubble_node(bid, subgraph):

    (xpos, ypos) = graph_center(subgraph)
    bnode = {"nodeid": "snp", "id": bid, "x": xpos, "y": ypos, "group": 12, "description": "desc", "size": 15}
    
    bubbleNode = new_subgraph()
    bubbleNode["subgraph"] = subgraph
    bubbleNode["nodes"].append(bnode)
    return bubbleNode

def add_bubble_subgraph(bubble, graph):
    bid = "b"+str(bubble["id"])
    subgraph = dict()
    insideIds = []

    #loop over every node inside the bubble
    for nodeId in bubble["inside"]:
        if nodeId in graph:
            subgraph[nodeId] = graph.pop(nodeId)
            insideIds.extend([node["id"] for node in subgraph[nodeId]["nodes"]])

    

    bubbleGraph = generate_bubble_node(bid, subgraph)

    #redraw links to bubble
    for nodeId in bubble["ends"]:

        for link in graph[nodeId]["toLinks"]:
            if link["target"] in insideIds:
                link["target"] = bid
                bubbleGraph["fromLinks"].append(link)

        for link in graph[nodeId]["fromLinks"]:
            if link["source"] in insideIds:
                link["source"] = bid
                bubbleGraph["toLinks"].append(link)

    graph[bid] = bubbleGraph
    return graph

def replace_bubbles(graph, bubbles):

    for bubbleId in bubbles:

        if "parent_chain" in bubbles[bubbleId]:
            print(bubbles[bubbleId]["parent_chain"])
        
        for bubble in bubbles[bubbleId]["bubbles"]:

            if bubble["type"] == "super":
                graph = add_bubble_subgraph(bubble, graph)

    return graph



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
