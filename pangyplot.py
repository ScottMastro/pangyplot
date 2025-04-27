import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, make_response
from cytoband import get_cytoband 
from db.query.query_top_level import get_top_level
from db.query.query_annotation import query_gene_range,text_search_gene
from db.query.query_subgraph import get_subgraph
from db.query.query_all import query_all_chromosomes, query_all_genome
from db.query.query_metadata import query_samples

from argparser import parse_args


app = Flask(__name__)
script_dir = os.path.dirname(os.path.realpath(__file__))

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

@app.context_processor
def inject_ga_tag_id():
    load_dotenv()
    # Get the Google Analytics tag ID from the environment variable
    ga_tag_id = os.getenv('GA_TAG_ID', '')
    return dict(ga_tag_id=ga_tag_id)

@app.route('/default-genome', methods=['GET'])
def get_default_genome():

    genome = query_all_genome()
    if genome is None: genome ="???"
    
    return jsonify({"genome": genome})


@app.route('/select', methods=["GET"])
def select():
    genome = request.args.get("genome")
    chrom = request.args.get("chromosome")
    start = request.args.get("start")
    end = request.args.get("end")
    
    start = int(start)
    end = int(end)
    resultDict = dict()
    
    #print(f"Getting clusters for {genome}#{chrom}:{start}-{end}...")
    #resultDict = get_clusters(genome, chrom, start, end)
    #resultDict["detailed"] = False 

    #if abs(end-start) < 100_000:
    print(f"Making graph for {genome}#{chrom}:{start}-{end}...")
    rd2 = get_top_level(genome, chrom, start, end)
    for key in rd2:
        resultDict[key] = rd2[key] 
    resultDict["detailed"] = True 

    return resultDict, 200

@app.route('/samples', methods=["GET"])
def get_samples():
    samples = query_samples()    
    return samples, 200

@app.route('/genes', methods=["GET"])
def genes():
    genome = request.args.get("genome")
    chrom = request.args.get("chromosome")
    start = request.args.get("start")
    end = request.args.get("end")
    
    start = int(start)
    end = int(end)
    
    resultDict = {}
    genes = query_gene_range(genome, chrom, start, end)

    print(f"Getting genes in: {genome}#{chrom}:{start}-{end}")
    print(f"   Genes: {len(genes)}")

    resultDict["genes"] = genes
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
    noncanon_path = os.path.join(script_dir, "static", "annotations", "noncanonical.txt")
    with open(noncanon_path) as file:
        for line in file.readlines():
            chromosomes.append(line)
    
    return chromosomes, 200

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
