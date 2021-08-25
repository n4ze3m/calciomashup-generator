from flask import request, jsonify,Flask
from mixer import generate
from flask_cors import CORS, cross_origin

app = Flask('')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/",methods=["GET"])
@cross_origin()
def home():
	return("Hello World")


@app.route("/api/generate", methods=["POST"])
@cross_origin()
def make():

	data = request.json
	t1Id = data["t1"]
	t2Id = data["t2"]
	return jsonify(generate(t1Id, t2Id))

app.run(host="0.0.0.0", port=8080)