Para cargar el JSON como grafo de networkx:

import json

import networkx as nx

G = nx.node_link_graph(json.load(open('PATH_JSON')))
