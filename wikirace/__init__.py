import os
from flask import Flask, render_template, request, jsonify
import requests

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'wikirace.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def main():
        return render_template("index.html")

    @app.route('/suggest')
    def suggest():
        query = request.args.get('q', '')
        if not query:
            return jsonify([])

        res = requests.get("https://en.wikipedia.org/w/api.php", {
            "action": "opensearch",
            "search": query,
            "limit": 5,
            "namespace": 0,
            "format": "json"
        })
        data = res.json()
        suggestions = data[1]
        return jsonify(suggestions)
    
    @app.route('/solve')
    def solve():
        pass

    return app
