import os
from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import requests
from wikirace.solver import crawl

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
        limit = int(request.args.get('l','1'))
        if not query:
            return jsonify([])

        res = requests.get("https://en.wikipedia.org/w/api.php", {
            "action": "opensearch",
            "search": query,
            "limit": limit,
            "namespace": 0,
            "format": "json"
        })
        data = res.json()
        suggestions = data[1],data[3]
        return jsonify(suggestions)
    
    @app.route('/crawl')
    def crawl_route():
        start_url = request.args.get('start')
        target_url = request.args.get('target')
    
        if not start_url or not target_url:
            return jsonify({'error': 'start and target are required'}), 400
    
        if not start_url.startswith('/wiki/') or not target_url.startswith('/wiki/'):
            return jsonify({'error': 'URLs must start with /wiki/'}), 400
    
        path = crawl(start_url, target_url)
        if path:
            return jsonify({'path': path}), 200
        else:
            return jsonify({'error': 'Path not found'}), 404
        
    
    @app.route('/solve')
    def solve():
        start_query = request.args.get('start')
        target_query = request.args.get('target')
        return render_template('solve.html', start=start_query, target=target_query)

    return app
