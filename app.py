from flask import Flask, render_template, request, make_response, redirect
from cytoband import get_cytoband 

app = Flask(__name__)


@app.route('/select', methods=["chromosome"])
def select():
    chromosome = request.args.get("chromosome")
    start = request.args.get("start")
    end = request.args.get("end")


    resultDict = dict()
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