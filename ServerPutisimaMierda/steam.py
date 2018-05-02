import json

from flask import Flask, render_template
import networkx as nx

app = Flask(__name__)

G = nx.node_link_graph(json.load(open('../data/extended_data.json')))


'''
@app.route('/node/<string:node_id>')
def node(node_id):
    return str(json.dumps(
        nx.node_link_data(nx.subgraph(G, nx.neighbors(G, node_id)))))
'''


@app.route('/node/<string:node_id>')
def node(node_id):
    return str(json.dumps(
        nx.node_link_data(nx.edge_subgraph(G,
                                           list(nx.edges(G, node_id))[:20]))))


@app.route('/top/games')
def top_games():
    return str(json.dumps(
        nx.node_link_data(
            nx.subgraph(
                G, [n[0] for n in sorted(
                    [(n, G.node[n]) for n in G.node
                     if G.node[n]['type'] == 'game'],
                    key=lambda n: n[1]['played_total_mins'],
                    reverse=True)[:10]]))))


@app.route('/')
def root():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
