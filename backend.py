from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route("/get_title")
def get_title():
    title = "My Valencia Travel Guide - From Backend!"
    return jsonify({"title": title})

@app.route("/")
def hello_world():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(debug=True)
