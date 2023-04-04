from cgitb import small
from math import floor
#import gfapy
import subprocess
import json

from cytoband import X
from segment import SimpleSegment,Bubble


GFATOOLS="/home/scott/bin/gfatools/gfatools"
ODGI="/home/scott/bin/odgi/bin/odgi"

OG="./static/data/chr6.pan.fa.a2fb268.4030258.b5c839f.smooth.gfa.og"

COLLAPSE_SIMPLE = True

def get_id(nodeId, side=0):
    return str((int(nodeId)-1)*2 + side)
def get_node(id):
    return str(floor(int(id)/2)+1)



def add_nodes(file, skipFirst=True):

    def get_node(id):
        return str(floor(int(id)/2)+1)

    graph = dict()
    with open(file) as t:
        for line in t:
            if skipFirst:
                skipFirst=False
            else:
                # idx,X,Y,component
                cols = line.strip().split("\t")
                id = cols[0]
                xpos = float(cols[1])*10
                ypos = float(cols[2])*5
                
                nodeId =  get_node(id)

                if nodeId not in graph:
                    node = SimpleSegment(nodeId, group=3, description="desc", size=3)
                    node.add_source_node(xpos,ypos)
                    graph[nodeId] = node
                else:
                    graph[nodeId].add_sink_node(xpos,ypos)
    return graph

def add_links(file, graph):

    #todo: flip direction for "negative" strand ex 2078

    with open(file) as f:
        for line in f:
            cols = line.split("\t")
            if cols[0] == "L":
                nodeIdFrom = cols[1] ; nodeIdTo = cols[3]
                nodeFrom = graph[nodeIdFrom]
                nodeTo = graph[nodeIdTo]

                nodeFrom.add_link_to(nodeTo)
                nodeTo.add_link_from(nodeFrom)

    return(graph)


def replace_bubbles(file, graph):

    bubbles={}
    with open(file) as f:
        bubbleJson = json.load(f)

    bubble_count = {}
    for bubbleId in bubbleJson:
        for bubble in bubbleJson[bubbleId]["bubbles"]:

            if bubble["type"] == "super":
                print(bubble)
                for nodeId in bubble["inside"]:
                    if nodeId not in bubble_count:
                        bubble_count[nodeId] = 0
                    bubble_count[nodeId]+=1

                bid = "bubble_" + str(bubble["id"])
                
                subgraph = []
                for nodeId in bubble["inside"]:
                    subgraph.append(graph[nodeId])
                source = graph[bubble["ends"][0]]
                sink = graph[bubble["ends"][1]]

                bubble = Bubble(bid, source, sink, subgraph, 
                                group=2, description="desc", size=5)

                bubbles[bid] = bubble

    return bubbles


def group_bubble(bubbles):
    bubble_dict = {}

    def remove_from_bubble_dict(bubble):
        for segment in bubble.subgraph:
            bubble_dict[segment.id].remove(bubble.id)


    for bid in bubbles:
        bubble = bubbles[bid]
        for node in bubble.subgraph:
            if node.id not in bubble_dict:
                bubble_dict[node.id] = []
            bubble_dict[node.id].append(bid)
    

    for id in bubble_dict:
        while len(bubble_dict[id]) > 1:
            print("before")
            print(bubble_dict[id])
            smallest = None
            for bid in bubble_dict[id]:
                if smallest is None or len(bubbles[bid].subgraph) < len(smallest.subgraph):
                    print(bid)
                    smallest = bubbles[bid]
            
            remove_from_bubble_dict(smallest)
            print("after")
            print(bubble_dict[id])





    return bubbles



def annotate_graph(bubbles, graph):
    
    for bid in bubbles:
        bubble = bubbles[bid]
        for node in bubble.subgraph:
            graph[node.id].group +=1

    return graph

    
def replace_superbubbles(file, graph):

    with open(file) as f:
        bubbles = json.load(f)

    for bubbleId in bubbles:
        for bubble in bubbles[bubbleId]["bubbles"]:
            
            if bubble["type"] == "super":
                bid = "bubble_" + str(bubble["id"])
                
                nodes = []
                for nodeId in bubble["inside"]:
                    nodes.append(graph.pop(nodeId))

                node = Segment(bid, group=2, description="desc", size=5,
                        subgraph=nodes)

                for nodeId in bubble["inside"]:
                    graph[nodeId] = PointerSegment(nodeId, node)



                graph[bid] = node

    return graph

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

def create_graph(layout, gfa):
    
    nodes = dict()
    links = dict()

    #nodeToBubble = node_to_bubble_dict(bubbles)
    #bubbleGraph = init_bubble_graphs(nodeToBubble)

    for nodeId in layout:
        
        nodes[nodeId] = {"nodes": [], "links": []}

        e = layout[nodeId]
        id1 = get_id(nodeId,0)
        id2 = get_id(nodeId,1)

        n1 = {"nodeid": nodeId, "id": id1, "x": e["x1"], "y": e["y1"], "group": 3, "description": "desc", "size": 3}
        n2 = {"nodeid": nodeId, "id": id2, "x": e["x2"], "y": e["y2"], "group": 3, "description": "desc", "size": 3}
        link = {"source": id1, "target": id2, "group": 3, "width": 10, "length":distance(e), "type": "node"}

        nodes[nodeId] = {"nodes": [n1,n2], "links": [link]}

    for nodeId in gfa:
        for nodeIdTo in gfa[nodeId]["to"]:

            link = {"source": get_id(nodeId, 1), "target": get_id(nodeIdTo, 0),
                        "group": 2, "width": 1, "length": 30, "type": "edge"}

            if nodeId not in links:
                links[nodeId] = {"to": [], "from": [] }



            if COLLAPSE_SIMPLE and nodeIdTo in nodeToBubble:
                for bid in nodeToBubble[nodeIdTo]:
                    bubbleGraph[bid]["links"].append(link)
            elif COLLAPSE_SIMPLE and nodeId in nodeToBubble:
                for bid in nodeToBubble[nodeId]:
                    bubbleGraph[bid]["links"].append(link)

            else:
                links.append(link)
    
    return links, bubbleGraph


        #if COLLAPSE_SIMPLE and nodeId in nodeToBubble:

        #    for bid in nodeToBubble[nodeId]:
        #        bubbleGraph[bid]["nodes"].extend([n1,n2])
        #        bubbleGraph[bid]["links"].append(link)
        #else:
        #    nodes.append(n1)
        #    nodes.append(n2)
        #    nodeLinks.append(link)

    return nodes, nodeLinks, bubbleGraph

def create_links(graph, bubbles, bubbleGraph):

    nodeToBubble = node_to_bubble_dict(bubbles)
    
    links = []
    for nodeId in graph:
        for nodeIdTo in graph[nodeId]["to"]:

            link = {"source": get_id(nodeId, 1), "target": get_id(nodeIdTo, 0),
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


def replace_bubbles2(bubbles, bubbleGraph):

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












def distance(node1, node2):
    return ((node2["x"] - node1["x"])**2 + (node2["y"] - node1["y"])**2)**0.5













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



def link_dict_old(file):
    links = dict()

    #todo: flip direction for "negative" strand ex 2078

    with open(file) as f:
        for line in f:
            cols = line.split("\t")
            if cols[0] == "L":
                nodeIdFrom = cols[1] ; nodeIdTo = cols[3]
                link = {"source": get_id(nodeIdFrom, 1), "target": get_id(nodeIdTo, 0),
                            "group": 2, "width": 1, "length": 30, "type": "edge"}

                if nodeIdFrom not in links:
                    links[nodeIdFrom] = {"to": [], "from": []}
                if nodeIdTo not in links:
                    links[nodeIdTo] = {"to": [], "from": []}

                links[nodeIdFrom]["to"].append(link)
                links[nodeIdTo]["from"].append(link)

    return(links)
def nodes_dict_old(file, skipFirst=True):

    nodes = dict()
    with open(file) as t:
        for line in t:
            if skipFirst:
                skipFirst=False
            else:
                # idx,X,Y,component
                cols = line.strip().split("\t")
                id = cols[0]
                xpos = float(cols[1])*10
                ypos = float(cols[2])*5

                nodeId =  get_node(id)
                
                node = {"nodeid": nodeId, "id": id, "x": xpos, "y": ypos, "group": 3, "description": "desc", "size": 3}

                if nodeId not in nodes:
                    nodes[nodeId] = {"nodes": [], "links": []}
                
                nodes[nodeId]["nodes"].append(node)

    for nodeId in nodes:
        n1,n2= nodes[nodeId]["nodes"]
        link = {"source": n1["id"], "target": n2["id"], "group": 3, "width": 10, "length":distance(n1,n2), "type": "node"}
        nodes[nodeId]["links"].append(link)

    return nodes