from math import floor
#import gfapy
import subprocess
import pandas as pd
import json

GFATOOLS="/home/scott/bin/gfatools/gfatools"
ODGI="/home/scott/bin/odgi/bin/odgi"
#GFA="./static/data/chr18.smooth.final.gfa"
#TSV="./static/data/chr18.smooth.final.tsv"

TSV = "static/data/DRB1-3123_sorted.lay.tsv"
GFA = "static/data/DRB1-3123_sorted.gfa"
BUBBLE= "static/data/DRB1-3123_sorted.bubble.json"


OG="./static/data/chr6.pan.fa.a2fb268.4030258.b5c839f.smooth.gfa.og"

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



def tsv_layout(tsv):

    nodes = []
    skipFirst=True
    with open(tsv) as t:
        for line in t:
            if skipFirst:
                skipFirst=False
            else:
                cols = line.strip().split("\t")
                i = int(cols[0])
                node = {"id": i, "nodeid": floor(i/2)+1, "x": float(cols[1])*10, "y": float(cols[2])*5,
                    "group": 3, "description": "desc", "size": 3}
                nodes.append(node)

    return nodes

def distance(n1, n2):
    return ((n2["x"] - n1["x"])**2 + (n2["y"] - n1["y"])**2)**0.5


def create_edges(nodes, gfa):
    edges = []
    node_dict = dict()
    for node in nodes:
        nodeid = node["nodeid"]
        if nodeid not in node_dict:
            node_dict[nodeid] = [node]
        else:
            node_dict[nodeid].append(node)

    for i,node in enumerate(nodes):
        if i % 2 == 0 :
            d = {"source": node["id"], "target": nodes[i+1]["id"],
                    "group": 3, "width": 10, "length":distance(node, nodes[i+1]), "type": "node"}
            edges.append(d)


    #todo: flip direction for "negative" strand ex 2078

    with open(gfa) as g:
        for line in g:
            cols = line.split("\t")
            if cols[0] == "L":
                n1 = int(cols[1]) ; n2 = int(cols[3])

                source = node_dict[n1][1]["id"]
                target = node_dict[n2][0]["id"]
                d = {"source": source, "target": target, "group": 2, "width": 1, "length": 30, "type": "edge"}
                edges.append(d)
                
    return(edges)

def bubble_json(file):

    with open(file) as f:
        bubbles = json.load(f)
        return bubbles

def poke_bubbles(nodes, links, bubbles):
    ends = set()
    colour = dict()
    for i in bubbles:
        bubble = bubbles[i]
        
        print("---------------------------")

        # simple, insertion, super
        for b in bubble["bubbles"]:
            print(b)
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