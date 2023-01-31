from flask import Flask, render_template, request, make_response, redirect
from cytoband import get_cytoband 

app = Flask(__name__)

@app.route('/cytoband', methods=["GET"])
def cytobands():
    chromosome = request.args.get("chromosome")
    resultDict = get_cytoband(chromosome)
    return resultDict, 200

@app.route('/')
def index():
    content = dict()
    response = make_response(render_template("index.html", **content ))
    return response

app.run()