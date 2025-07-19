from flask import Flask, render_template, request, jsonify, make_response
from dotenv import load_dotenv

import os, cytoband
import db.neo4j.neo4j_db as db
from db.query.query_top_level import get_top_level
from db.query.query_annotation import query_gene_range,text_search_gene
from db.query.query_subgraph import get_subgraph, get_segments_in_range
from db.query.query_all import query_all_chromosomes, query_all_genome
from db.query.query_path import query_paths

from db.query.query_metadata import query_samples
from db.utils import gfa_writer as gfaer

app = Flask(__name__)

DEFAULT_DB = "default"
DEFAULT_PORT = 5700

def initialize_app(db_name=None, port=None, development=True):
    load_dotenv()

    organism = os.getenv("ORGANISM", "human")
    cytoband_path = os.getenv("CYTOBAND_PATH")
    canonical_path = os.getenv("CANONICAL_PATH")
    db_name = db_name or os.getenv("DB_NAME", DEFAULT_DB)

    if organism == "custom":
        if not cytoband_path or not canonical_path:
            print("No information about CYTOBAND_PATH or CANONICAL_PATH was found in .env")
            organism = "human"
    else:
        cytoband_path = None
        canonical_path = None

    cytoband.set_cytoband(organism, cytoband_path, canonical_path)
    db.db_init(db_name)

    if development:
        port = port if port else DEFAULT_PORT
        print(f"Starting PangyPlot (non-production environment)... http://127.0.0.1:{port}")
        app.run(port=port)
    
    return app

@app.context_processor
def inject_ga_tag_id():
    load_dotenv()
    # Get the Google Analytics tag ID from the environment variable
    ga_tag_id = os.getenv('GA_TAG_ID', '')
    return dict(ga_tag_id=ga_tag_id)

@app.route('/default-genome', methods=['GET'])
def get_default_genome():

    genome = query_all_genome(top_result=True)
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
    uuid = request.args.get("uuid")
    genome = request.args.get("genome")
    chrom = request.args.get("chromosome")
    start = request.args.get("start")
    end = request.args.get("end")

    start = int(start)
    end = int(end)

    print(f"Getting subgraph for {uuid}...")

    resultDict = get_subgraph(uuid, genome, chrom, start, end)
    return resultDict, 200

@app.route('/chromosomes', methods=["GET"])
def chromosomes():
    genome = request.args.get("genome")

    canonical = cytoband.get_canonical()
    noncanonicalOnly = request.args.get('noncanonical', 'false').lower() == 'true'
    
    chromosomes = query_all_chromosomes()
    if noncanonicalOnly:
        chromosomes = [chrom for chrom in chromosomes if chrom.split("#")[-1] not in canonical]
        
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

    resultDict = cytoband.get_cytoband(chromosome)
    return resultDict, 200

@app.route('/gfa', methods=["GET"])
def gfa():
    genome = request.args.get("genome")
    chromosome = request.args.get("chromosome")
    start = request.args.get("start")
    end = request.args.get("end")

    nodes, links = get_segments_in_range(genome, chromosome, start, end)
    gfa_lines = [gfaer.get_gfa_header()]

    for node in nodes:
        gfa_lines.append(gfaer.get_s_line(node))

    for link in links:
        gfa_lines.append(gfaer.get_l_line(link))

    node_ids = {n["id"] for n in nodes}
    collection = nodes[0]["collection"] if nodes else None
    paths = query_paths(node_ids, collection)

    for path in paths:
        gfa_lines.append(gfaer.get_p_line(path))
        
    gfa_text = "\n".join(gfa_lines)

    response = make_response(gfa_text)
    response.headers['Content-Type'] = 'text/plain'
    response.headers['Content-Disposition'] = 'attachment; filename=graph.gfa'
    return response

@app.route('/')
def index():
    content = dict()
    response = make_response(render_template("index.html", **content ))
    return response