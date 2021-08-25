import flask
from flask import request, jsonify
from mixer import *

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route("/",methods=["GET"])

def home():
	return("Hello World")


@app.route("/api/generate", methods=["POST"])

def make():

	data = request.json
	t1Id = data["t1Id"]
	t2Id = data["t2Id"]
	return jsonify(generate(t1Id, t2Id))
	
app.run()