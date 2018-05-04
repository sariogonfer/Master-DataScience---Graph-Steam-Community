import json

from flask import Flask, render_template
import networkx as nx

app = Flask(__name__)

G = nx.node_link_graph(json.load(open('./static/data/graph.json')))
G_uu = G.edge_subgraph([(u, gm) for u, gm, t in G.edges(data='type')
                        if t == 'is_friend'])
extended_games = dict()

for l in open('../data/extended_games.json'):
    extended_games.update(json.loads(l))


@app.route('/node/<string:node_id>')
def node(node_id):
    return str(json.dumps(
        nx.node_link_data(nx.edge_subgraph(G,
                                           list(nx.edges(G, node_id))[:20]))))


@app.route('/games/<string:game_id>')
def game(game_id):
    return str(json.dumps(extended_games[game_id]))


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


@app.route('/genres/<string:g>/topGames')
def genre_top_games(g):
    from collections import Counter
    c = Counter({id_: data['played_total_mins']
                 for id_, data in G.nodes(data=True)
                 if data['type'] == 'game' and 'genres' in data
                 and g in data['genres']})
    if len(c) < 20:
        return c.most_common(20)
    return c.most_common(20) + [('others',
                                 sum(v for _, v in c.most_common()[20:]))]


@app.route('/genres/')
def genres():
    from collections import Counter
    c = Counter({genre: G.node[id_]['played_total_mins']
                 for id_, data in G.nodes(data=True)
                 if data['type'] == 'game' and 'genres' in data
                 for genre in G.node[id_]['genres']})
    return json.dumps(
        {'name': 'genres', 'children': [
            {'name': k, 'value': v,
             'children': [{
                 'name': G.node[id_]['name'] if id_ != 'others' else 'others',
                 'value': v, 'steamid': id_,
                 'logo': "http://media.steampowered.com/steamcommunity/public/images/apps/{}/{}.jpg".format(
                               id_, G.node[id_]['img_logo_url'])
                 if id_ != 'others'
                 else 'https://steamstore-a.akamaihd.net/public/shared/images/header/globalheader_logo.png?t=962016'}
                          for id_, v in genre_top_games(k)]}
        for k, v in c.items()]})


@app.route('/genres/<string:g>')
def genre(g):
    from collections import Counter
    c = Counter([genre for id_, data in G.nodes(data=True)
                 if data['type'] == 'game' and 'genres' in data
                 and g in data['genres']
                 for genre in G.node[id_]['genres']])
    return json.dumps({'name': 'genres', 'children': [
        {'name': k, 'value': v, 'children': '/genres/{}'.format(k)} for k, v
        in c.items()]})


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


@app.route('/')
def root():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
