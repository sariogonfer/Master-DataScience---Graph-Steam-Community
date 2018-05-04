import json

from flask import Flask, render_template
import networkx as nx

app = Flask(__name__)

G = nx.node_link_graph(json.load(open('../data/extended_data.json')))
G_uu = G.edge_subgraph([(u, gm) for u, gm, t in G.edges(data='type')
                        if t == 'is_friend'])

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


@app.route('/user/<string:user_id>')
def user(user_id):
    print(user_id)
    friends = {u for f in G_uu.neighbors(user_id)
               for u in G_uu.neighbors(f)}
    # games = set(G_ug.neighbors('76561198083091304'))
    my_copy = G.subgraph(friends).copy()
    pagerank = nx.pagerank(my_copy, weight='played_hours')
    max_pagerank = max(pagerank.values())
    pagerank = {k: (v / max_pagerank) for k, v in pagerank.items()}
    nx.set_node_attributes(my_copy, pagerank, 'pagerank')
    del pagerank, max_pagerank
    betweenness = nx.betweenness_centrality(my_copy)
    max_betweenness = max(betweenness.values())
    betweenness = {k: (v / max_betweenness) for k, v in betweenness.items()}
    nx.set_node_attributes(my_copy, betweenness, 'betweenness')
    del betweenness, max_betweenness
    closeness = nx.closeness_centrality(my_copy)
    max_closeness = max(closeness.values())
    closeness = {k: (v / max_closeness) for k, v in closeness.items()}
    nx.set_node_attributes(my_copy, closeness, 'closeness')
    del closeness, max_closeness
    degree = nx.degree_centrality(my_copy)
    max_degree = max(degree.values())
    degree = {k: (v / max_degree) for k, v in degree.items()}
    nx.set_node_attributes(my_copy, degree, 'degree_centrality')
    del degree, max_degree
    return json.dumps(nx.node_link_data(my_copy))


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
