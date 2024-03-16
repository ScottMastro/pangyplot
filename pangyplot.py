from flask import Flask, render_template, request, jsonify, make_response
from cytoband import get_cytoband 
from db.neo4j_db import update_db
from db.query.query_top_level import get_top_level
from db.query.query_annotation import get_genes_in_range,text_search_gene
from db.query.query_subgraph import get_subgraph
from db.query.query_all import query_all_chromosomes, query_all_db
from argparser import parse_args

app = Flask(__name__)

'''
@app.route('/dbset')
def set_db():
    db = request.args.get("db")
    update_db(db)
    return

@app.route('/dboptions')
def get_db_options():
    dbs = query_all_db()
    if len(dbs)> 0:
        update_db(dbs[0])

    return jsonify(dbs)
'''

@app.route('/select', methods=["GET"])
def select():
    genome = request.args.get("genome")
    chrom = request.args.get("chromosome")
    start = request.args.get("start")
    end = request.args.get("end")
    print(f"Making graph for {genome}#{chrom}:{start}-{end}...")
    
    start = int(start)
    end = int(end)

    resultDict = get_top_level(genome, chrom, start, end)
    
    return resultDict, 200

@app.route('/genes', methods=["GET"])
def genes():
    genome = request.args.get("genome")
    chrom = genome + "#" + request.args.get("chromosome")
    start = request.args.get("start")
    end = request.args.get("end")
    print(f"Getting genes in {chrom}:{start}-{end}...")
    
    start = int(start)
    end = int(end)
    
    resultDict = {}
    resultDict["genes"] = get_genes_in_range(chrom, start, end)
    resultDict["annotations"] = []

    return resultDict, 200

@app.route('/subgraph', methods=["GET"])
def subgraph():
    nodeid = request.args.get("nodeid")
    genome = request.args.get("genome")
    chrom = request.args.get("chromosome")
    start = request.args.get("start")
    end = request.args.get("end")

    start = int(start)
    end = int(end)

    print(f"Getting subgraph for {nodeid}...")

    nodeid = int(nodeid)
    resultDict = get_subgraph(nodeid, genome, chrom, start, end)
    return resultDict, 200

@app.route('/chromosomes', methods=["GET"])
def chromosomes():
    genome = request.args.get("genome")

    canonical = [f"chr{n}" for n in range(1, 23)] + ["chrX", "chrY"]
    noncanonicalOnly = request.args.get('noncanonical', 'false').lower() == 'true'
    
    chromosomes = query_all_chromosomes()
    if noncanonicalOnly:
        chromosomes = [chrom for chrom in chromosomes if chrom.split("#")[-1] not in canonical]
    
    # TODO: make real
    with open("./static/annotations/noncanonical.txt") as file:
        for line in file.readlines():
            chromosomes.append(line)
    
    return chromosomes, 200


@app.route('/haplotypes', methods=["GET"])
def haplotypes():

    resultDict={}
    return resultDict, 200

@app.route('/search')
def search():
    type = request.args.get('type')
    query = request.args.get('query')
    
    results = []

    if type == "gene":
        results = text_search_gene(query)
        for gene in results:
            gene["name"] = gene["gene"]

    return jsonify(results)


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
    parse_args(app)