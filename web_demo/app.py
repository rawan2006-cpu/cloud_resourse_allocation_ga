# web_demo/app.py
from flask import Flask, request, render_template, jsonify
import threading
from src.experiments.runner import example_run

app = Flask(__name__)

@app.route("/")
def index():
    return "<h2>Cloud GA Demo - Run experiments using /run endpoint</h2>"

@app.route("/run", methods=["POST"])
def run_experiment():
    # runs example_run in background thread to avoid request timeout (for demo only)
    thread = threading.Thread(target=example_run)
    thread.start()
    return jsonify({"status":"started"}), 202

if __name__ == "__main__":
    app.run(debug=True, port=5000)
