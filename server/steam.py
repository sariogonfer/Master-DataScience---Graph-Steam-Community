import json

from flask import Flask, render_template
import networkx as nx

app = Flask(__name__)

G = nx.node_link_graph(json.load(open('data.json')))

@app.route('/node/<string:node_id>')
def node(node_id):
    return str(json.dumps(
        nx.node_link_data(nx.subgraph(G, nx.neighbors(G, node_id)))))

@app.route('/')
def root():
    return '\n'.join(open('index.html').readlines())

if __name__ == '__main__':
    app.run()
