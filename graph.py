import json
import os
import sys

import networkx.algorithms.community.label_propagation as lp
import networkx as nx
import matplotlib.pyplot as plt
import csv
import sys
import operator
from networkx.readwrite import json_graph
import datetime
import pycountry

def get_country_code(name):
    try:
        return pycountry.countries.get(alpha_2=name).common_name
    except:
        try:
            return pycountry.countries.get(alpha_2=name).name
        except:
            return 'Unknown'

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Función para imprimir texto con \n o sin \n al final de la linea
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ARGUMENTOS
# text:         Texto a imprimir
# print_ln:     Booleano que determina si imprimir un salto de linea al final
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def special_print(text, print_ln = True):
    if (print_ln):
        print(text)
    else:
        sys.stdout.write(text)
        sys.stdout.flush()

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Método para devolver, en función del tipo, el contenido de un atributo de un json
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ARGUMENTOS
# json:         Fichero json
# element:      Atributo a obtener
# type:         Tipo de dato (string/boolean/list)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# RETORNO
# text:        Elemento buscado
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_element(json, element, type='string'):
    if (type == 'string'):
        return json[element] if element in json else ''
    elif (type == 'boolean'):
        return json[element] if element in json else False
    elif (type == 'list'):
        return json[element] if element in json else []

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Lectura y almacenamiento de información de usuarios al grafo pasado por argumento
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ARGUMENTOS
# graph:        Grafo en el que volcar la información de usuarios
# path:         Ruta al fichero user.json
# debug:        Booleano que indica si mostrar información debug
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# RETORNO
# graph:        Grafo
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def load_users(graph, path='./output/', debug=False):
    with open(path + 'user.json', 'r') as f:

        for user in f:
            try:
                user_json = json.loads(user)
                player = user_json['response']['players'][0]

                loccountry = get_element(player, 'loccountrycode')

                #Creacion de nodo
                graph.add_node(
                    # Id
                    player['steamid'],
                    # Tipo de nodo
                    type            ='user',
                    profileurl      = get_element(player, 'profileurl'),
                    realname        = get_element(player, 'realname'),
                    loccountrycode  = loccountry,
                    country         = get_country_code(loccountry),
                    avatar          = get_element(player, 'avatar'),
                    avatar_medium   = get_element(player, 'avatarmedium'),
                    avatar_full     = get_element(player, 'avatarfull'),
                    timecreated     = get_element(player, 'timecreated'),
                    lastlogoff      = get_element(player, 'lastlogoff'),
                    #Nombre de usuario
                    name            = get_element(player, 'personaname'))

            except ValueError:
                if (debug):
                    print ('ERROR Decoding USER json failed')


    return graph


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Lectura y almacenamiento de relaciones entre usuarios al grafo pasado por argumento
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ARGUMENTOS
# graph:        Grafo en el que volcar la información
# path:         Ruta al fichero user_user_rels.csv
# debug:        Booleano que indica si mostrar información debug
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# RETORNO
# graph:        Grafo
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def load_user_relations(graph, path='./output/', debug=False):
    with open(path + 'user_user_rels.csv', 'r') as f:
        csv_reader = csv.reader(f, delimiter=',')

        for relation in csv_reader:
            if (relation[0] in graph and relation[1] in graph):
                #Incluimos relaciones de tipo is_friend entre dos usuarios
                graph.add_edge(relation[0], relation[1],
                    type='is_friend')
            else:
                if (debug):
                    if (not(relation[0] in graph)):
                        print('WARNING: USER %s not exist' % relation[0])
                    if (not(relation[1] in graph)):
                        print('WARNING: USER %s not exist' % relation[1])

    return graph

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Lectura y almacenamiento de información de juegos al grafo pasado por argumento
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ARGUMENTOS
# graph:        Grafo en el que volcar la información de juegos
# path:         Ruta al fichero games.json
# debug:        Booleano que indica si mostrar información debug
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# RETORNO
# graph:        Grafo
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def load_games(graph, path='./output/', debug=False):
    with open(path + 'games.json', 'r') as f:
    #with open(path + 'extended_games.json', 'r') as f:

        for game_f in f:
            try:
                game = json.loads(game_f)

                #Creación de nodo
                graph.add_node(
                    #Id
                    str(game['appid']),
                    #Tipo de nodo: Juego
                    type                        ='game',
                    # Nombre del juego
                    name                        = get_element(game, 'name'),
                    img_icon_url                = get_element(game, 'img_icon_url'),
                    img_logo_url                = get_element(game, 'img_logo_url'),
                    genres                      = get_element(game, 'genres', type='list'),
                    has_community_visible_stats = get_element(game, 'has_community_visible_stats', type='boolean'))

            except ValueError:
                if (debug):
                    print ('ERROR Decoding GAME json failed')

    return graph


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Lectura y almacenamiento de relaciones entre usuarios y juegos al grafo pasado por argumento
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ARGUMENTOS
# graph:        Grafo en el que volcar la información
# path:         Ruta al fichero user_game_rels.csv
# debug:        Booleano que indica si mostrar información debug
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# RETORNO
# graph:        Grafo
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def load_game_relations(graph, path='./output/', debug=False):
    with open(path + 'user_game_rels.csv', 'r') as f:
        csv_reader = csv.reader(f, delimiter=',')

        for relation in csv_reader:
            if (relation[0] in graph and relation[1] in graph):
                #Incluimos relaciones de tipo plays entre usuario y juego
                #0: origen; 1: destino; 2: horas jugadas
                graph.add_edge(relation[0], relation[1],
                    type='plays',
                    played_mins=int(relation[2]))
            else:
                if (debug):
                    if (not(relation[0] in graph)):
                        print('WARNING: USER %s not exist' % relation[0])
                    if (not(relation[1] in graph)):
                        print('WARNING: GAME %s not exist' % relation[1])

    return graph

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Creación y carga de datos en el grafo
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ARGUMENTOS
# graph:        Grafo en el que volcar la información
# path:         Ruta al fichero user_game_rels.csv
# debug:        Booleano que indica si mostrar información debug
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# RETORNO
# graph:        Grafo
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def load_graph():
    g = nx.Graph()
    special_print("Leyendo usuarios.............................", print_ln=False)
    g = load_users(g)
    print("OK")
    special_print("Leyendo relaciones entre usuarios............", print_ln=False)
    g = load_user_relations(g)
    print("OK")
    special_print("Leyendo Juegos...............................", print_ln=False)
    g = load_games(g)
    print("OK")
    special_print("Leyendo relaciones entre usuarios y juegos...", print_ln=False)
    g = load_game_relations(g, debug = False)
    print("OK")
    return g

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Impresión por pantalla de información relevante del grafo
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ARGUMENTOS
# g:            Grafo en el que volcar la información
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def print_info(g):
    print("Es grafo conexo: " + str(nx.is_connected(g)))
    print(nx.info(g))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Volcado de grafo a fichero json
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ARGUMENTOS
# g:            Grafo
# type:         Tipo de nodo que se desea volcar (user/game)
# file:         Nombre del fichero
# n:            Numero de nodos que se quiere volcar
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def dump_nodes_into_file(g, type, file, n):
    #Escritura de subgrafo de juegos a fichero
    open(file, 'w').write(
        #Subgrafo a formato json
        json.dumps(json_graph.node_link_data(
            #Obtención del subgrafo
            g.subgraph(a for (a,b) in
                #200 nodos de tipo game (juegos) más importantes ordenados de mayor a menor importancia por criterio de pagerank
                sorted([node for node in g.nodes(data=True) if node[1]['type'] == type and 'pagerank_centrality' in node[1]],
                    # Ordenacion por atributo 'pagerank_centrality'
                    key=lambda t: t[1]['pagerank_centrality'], reverse=True)[:n]))))


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Volcado de grafo a fichero json para la visualización de circulos con zoom
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ARGUMENTOS
# g:            Grafo
# type:         Tipo de nodo que se desea volcar (user/game)
# file:         Nombre del fichero
# n:            Numero de nodos que se quiere volcar
# attribute:    Atributo por el que se agrupará
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def dump_circles_nodes_into_file(g, type, file, n, attribute, is_list = True):
    #Escritura de subgrafo de juegos a fichero
    games = {}

    #Recuperación de los n nodos más importantes
    top_nodes = sorted([node for node in g.nodes(data=True) if node[1]['type'] == type and 'pagerank_centrality' in node[1]],
                    # Ordenacion por atributo 'pagerank_centrality'
                    key=lambda t: t[1]['pagerank_centrality'], reverse=True)[:n]

    #Almacenamos la información en la variable games con el genero, nombre del juego y minutos jugados
    for node in top_nodes:
        if (node[1]['type'] == type):
            if (is_list):
                for attr in node[1][attribute]:
                    if (attr not in games):
                        games[attr] = {}
                    games[attr][node[1]['name']] = node[1]['played_total_mins']
            else:
                if (node[1][attribute] not in games):
                    games[node[1][attribute]] = {}
                games[node[1][attribute]][node[1]['name']] = node[1]['played_total_mins']

    #Volcado en el formato que espera el html de d3js
    output_lst = []

    for genre in games:
        genre_dict = {}
        genre_dict['name'] = genre
        genre_dict['children'] = []

        for game in games[genre]:
            game_dict = {}
            game_dict['name'] = game
            game_dict['size'] = games[genre][game]
            genre_dict['children'].append(game_dict)

        output_lst.append(genre_dict)

    output = {}
    output['name'] = '200'
    output['children'] = output_lst

    open(file, 'w').write(
        json.dumps(output))



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Programa principal. Main
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":

    print("#####################################################################################################################")
    print("                                                  LECTURA DE DATOS")
    print("#####################################################################################################################")
    g = load_graph()

    print("#####################################################################################################################")
    print("                                             CARACTERÍSTICAS DEL GRAFO")
    print("#####################################################################################################################")
    print_info(g)

    # Creación de subgrafo de usuarios (usuarios y relaciones entre usuarios)
    user_sg = g.subgraph([i for i in g.nodes() if (g.node[i]['type'] == 'user')])

    # Creación de subgrafo a partir de los nodos que tengan aristas/uniones de tipo 'plays'. Esto incluye relaciones entre usuarios y juegos
    # De esta forma no tenemos en cuenta relaciones de usuarios con usuarios.
    games_user_sg = g.edge_subgraph([(p, g) for (p, g, data) in g.edges(data=True) if (data['type'] == 'plays')])


    print("#####################################################################################################################")
    print("                                             30 JUGADORES QUE MÁS HAN JUGADO")
    print("#####################################################################################################################")

    # Almacenamos el grado de todos los nodos, tanto usuarios como juegos, como atributo.
    # El peso de las aristas de unión entre los usuarios y los juegos se almacena en el atributo 'played_mins'
    # y corresponde con los minutos jugados de ese usuario a ese juego.
    # Por lo tanto, si calculamos el grado teniendo en cuenta el peso, vamos a obtener el total
    # de minutos jugados para cada usuario. En el caso de los juegos, va a corresponder con los minutos
    # jugados por todos los usuarios a ese juego
    nx.set_node_attributes(g, dict(nx.degree(games_user_sg, weight = 'played_mins')), 'played_total_mins')

    users_more_played = sorted([node for node in g.nodes(data=True) if node[1]['type'] == 'user' and 'played_total_mins' in node[1]],
        key=lambda t: t[1]['played_total_mins'], reverse=True)[:30]

    for (user_id, info) in users_more_played:
        print("[Minutos jugados: %10d] Usuario: %s" % (info['played_total_mins'], info['name']))



    print("#####################################################################################################################")
    print("                                             30 JUGADORES QUE MÁS JUEGOS POSEEN")
    print("#####################################################################################################################")

    # Obtenemos el grado de los usuarios y juegos, sin tener en cuenta los minutos jugados, sino simplemente los enlaces
    # entre jugador y juego. De esta forma, obtendremos para los usuarios el número de juegos que tienen y para los juegos,
    # el número de usuarios que han jugado.
    nx.set_node_attributes(g, dict(nx.degree(games_user_sg)), 'degree')

    users_have_more_games = sorted([node for node in g.nodes(data=True) if node[1]['type'] == 'user' and 'degree' in node[1]],
        key=lambda t: t[1]['degree'], reverse=True)[:30]

    for (user_id, info) in users_have_more_games:
        print("[Juegos: %10d] Usuario: %s" % (info['degree'], info['name']))


    print("#####################################################################################################################")
    print("                                               30 JUGADORES CON MÁS AMIGOS")
    print("#####################################################################################################################")

    # Obtenemos el grado de los usuarios en el subgrafo user_sg. Ese subgrafo únicamente contiene usuarios, por lo que
    # el número de amigos de cada usuario se corresponderá con el grado sin tener en cuenta ningún peso.
    nx.set_node_attributes(g, dict(nx.degree(user_sg)), 'friends')

    users_friendship = sorted([node for node in g.nodes(data=True) if node[1]['type'] == 'user' and 'friends' in node[1]],
        key=lambda t: t[1]['friends'], reverse=True)[:30]

    for (user_id, info) in users_friendship:
        print("[Amigos: %4d] Usuario: %s" % (info['friends'], info['name']))


    print("#####################################################################################################################")
    print("                                             30 JUGADORES MÁS IMPORTANTES")
    print("                 (teniendo en cuenta el tiempo de juego y para todas las jugadas (utilizando Pagerank))")
    print("#####################################################################################################################")
    special_print("Ejecutando Pagerank. Por favor, espere...", print_ln=False)
    after = datetime.datetime.now()
    nx.set_node_attributes(g, dict(nx.pagerank(games_user_sg, weight = 'played_mins')), 'pagerank_centrality')
    print("OK")
    print("Tiempo de ejecución Pagerank: %.2f segundos" % (datetime.datetime.now() - after).total_seconds())
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    users_sorted_pagerank = sorted([node for node in g.nodes(data=True) if node[1]['type'] == 'user' and 'pagerank_centrality' in node[1]],
        key=lambda t: t[1]['pagerank_centrality'], reverse=True)[:30]

    for (user_id, info) in users_sorted_pagerank:
        print("[Importancia: %4f] Usuario: %s" % (info['pagerank_centrality'], info['name']))


    print("#####################################################################################################################")
    print("                                             30 JUEGOS MÁS IMPORTANTES")
    print("                 (teniendo en cuenta el tiempo de juego y para todas las jugadas (utilizando Pagerank))")
    print("#####################################################################################################################")

    games_sorted_pagerank = sorted([node for node in g.nodes(data=True) if node[1]['type'] == 'game' and 'pagerank_centrality' in node[1]],
        key=lambda t: t[1]['pagerank_centrality'], reverse=True)[:30]

    for (user_id, info) in games_sorted_pagerank:
        print("[Importancia: %4f] Juego: %s" % (info['pagerank_centrality'], info['name']))


    print("#####################################################################################################################")
    print("                                             30 JUGADORES MÁS IMPORTANTES")
    print("                 (teniendo en cuenta el tiempo de juego y para jugadas > 5 minutos (utilizando Pagerank))")
    print("#####################################################################################################################")
    # Creamos un subgrafo a partir de los nodos que tengan aristas/uniones de tipo 'plays' y que el atributo played_mins sea superior a 5.
    # Esto generará un subgrafo con los juegos y usuarios que hayan jugado a dichos juegos más de 5 minutos (o el valor de bottom_limit)
    bottom_limit = 5
    games_user_filtered_sg = g.edge_subgraph([(p, g) for (p, g, data) in g.edges(data=True) if (data['type'] == 'plays'and data['played_mins'] > bottom_limit)])

    special_print("Ejecutando Pagerank. Por favor, espere...", print_ln=False)
    after = datetime.datetime.now()
    # Almacenamos dicha centralidad en el atributo pagerank_filtered_centrality
    nx.set_node_attributes(g, dict(nx.pagerank(games_user_filtered_sg, weight = 'played_mins')), 'pagerank_filtered_centrality')
    print("OK")
    print("Tiempo de ejecución Pagerank: %.2f segundos" % (datetime.datetime.now() - after).total_seconds())
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    users_sorted_filtered_pagerank = sorted([node for node in g.nodes(data=True) if node[1]['type'] == 'user' and 'pagerank_filtered_centrality' in node[1]],
        key=lambda t: t[1]['pagerank_filtered_centrality'], reverse=True)[:30]

    for (user_id, info) in users_sorted_filtered_pagerank:
        print("[Importancia: %4f] Usuario: %s" % (info['pagerank_filtered_centrality'], info['name']))


    print("#####################################################################################################################")
    print("                                             30 JUEGOS MÁS IMPORTANTES")
    print("                 (teniendo en cuenta el tiempo de juego y para jugadas > 5 minutos (utilizando Pagerank))")
    print("#####################################################################################################################")

    games_sorted_filtered_pagerank = sorted([node for node in g.nodes(data=True) if node[1]['type'] == 'game' and 'pagerank_filtered_centrality' in node[1]],
        key=lambda t: t[1]['pagerank_filtered_centrality'], reverse=True)[:30]

    for (user_id, info) in games_sorted_filtered_pagerank:
        print("[Importancia: %4f] Juego: %s" % (info['pagerank_filtered_centrality'], info['name']))


    print("#####################################################################################################################")
    print("                SUBGRAFOS CON 1.000 USUARIOS QUE MÁS HAN JUGADO Y 1.000 USUARIOS QUE MENOS HAN JUGADO")
    print("#####################################################################################################################")

    # Obtenemos los 1000 usuarios que más han jugado de toda la red. En el atributo 'played_total_mins' de los usuarios (type == 'user') hemos
    # almacenado anteriormente el tiempo (en minutos) que han jugado
    top_users = sorted([node for node in g.nodes(data=True) if node[1]['type'] == 'user' and 'played_total_mins' in node[1]],
        key=lambda t: t[1]['played_total_mins'], reverse=True)[:1000]


    # Obtenemos los 1000 usuarios que menos han jugado de toda la red. En el atributo 'played_total_mins' de los usuarios (type == 'user') hemos
    # almacenado anteriormente el tiempo (en minutos) que han jugado. Eliminamos los que no hayan jugado ni siquiera 1 minuto
    bottom_users = sorted([node for node in g.nodes(data=True) if node[1]['type'] == 'user' and 'played_total_mins' in node[1] and (node[1]['played_total_mins'] > 0)],
        key=lambda t: t[1]['played_total_mins'], reverse=False)[:1000]

    # Generamos los subgrafos a partir de las aristas de tipo plays que salgan o entren de los usuarios y cuyo tipo sea plays
    # De esta forma el subgrafo contendrá los 1000 usuarios que más han jugado y los juegos a los que han jugado.
    top_users_sg = g.edge_subgraph([(a, b) for (a, b, data) in g.edges([user_id for (user_id, attrs) in top_users], data=True) if (data['type'] == 'plays')])
    # El subgrafo contendrá los 1000 usuarios que menos han jugado y los juegos a los que han jugado.
    bottom_users_sg = g.edge_subgraph([(a, b) for (a, b, data) in g.edges([user_id for (user_id, attrs) in bottom_users], data=True) if (data['type'] == 'plays')])

    output_dir = "./server/static/data"

    print("#####################################################################################################################")
    print("                                 VOLCADO DE INFORMACIÓN A FICHEROS PARA SU VISUALIZACION")
    print("#####################################################################################################################")
    special_print("Volcando 200 juegos más importantes.....", print_ln=False)
    dump_circles_nodes_into_file(g, 'game', os.path.join(output_dir, '200_main_games_bubble_zoom.json'), 200, 'genres')
    print("OK")
    special_print("Volcando 200 usuarios más importantes...", print_ln=False)
    dump_circles_nodes_into_file(g, 'user', os.path.join(output_dir, '200_main_users_bubble_zoom.json'), 200, 'country', is_list = False)
    print("OK")
    special_print("Exportando el grafo como JSON", print_ln=False)
    with open(os.path.join(output_dir, 'graph.json'), 'w') as f_:
        f_.write(json.dumps(nx.node_link_data(g)))
    print("OK")
