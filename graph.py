import networkx as nx
import json
import csv 

def get_element(json, element, type='string'):
    if (type == 'string'):
        return json[element] if element in json else ''
    elif (type == 'boolean'):
        return json[element] if element in json else False

def load_users(graph, path='./output/', debug=False):
    with open(path + 'user.json', 'r') as f:

        for user in f:
            try:
                user_json = json.loads(user)
                player = user_json['response']['players'][0]
                
                #Creating a new node
                graph.add_node(player['steamid'],
                    type            ='user',
                    profileurl      = get_element(player, 'profileurl'),
                    realname        = get_element(player, 'realname'),
                    loccountrycode  = get_element(player, 'loccountrycode'),
                    avatar          = {
                                        get_element(player, 'avatar'),
                                        get_element(player, 'avatarmedium'),
                                        get_element(player, 'avatarfull')
                                      },
                    timecreated     = get_element(player, 'timecreated'),
                    lastlogoff      = get_element(player, 'lastlogoff'),
                    personaname     = get_element(player, 'personaname'))
                    
            except ValueError:
                if (debug):
                    print ('ERROR Decoding USER json failed')


    return graph


def load_user_relations(graph, path='./output/', debug=False):
    with open(path + 'user_user_rels.csv', 'r') as f:
        csv_reader = csv.reader(f, delimiter=',')
        
        for relation in csv_reader:
            if (relation[0] in graph and relation[1] in graph):
                graph.add_edge(relation[0], relation[1])
            else:
                if (debug):
                    if (not(relation[0] in graph)):
                        print('WARNING: USER %s not exist' % relation[0])
                    if (not(relation[1] in graph)):
                        print('WARNING: USER %s not exist' % relation[1])
    
    return graph

def load_games(graph, path='./output/', debug=False):
    with open(path + 'games.json', 'r') as f:
        for game_f in f:
            try:
                game = json.loads(game_f)
                
                #Creating a new node
                graph.add_node(game['appid'],
                    type                        ='game',
                    name                        = get_element(game, 'name'),
                    img_icon_url                = get_element(game, 'img_icon_url'),
                    img_logo_url                = get_element(game, 'img_logo_url'),
                    has_community_visible_stats = get_element(game, 'has_community_visible_stats', type='boolean'))
                    
            except ValueError:
                if (debug):
                    print ('ERROR Decoding GAME json failed')
    
    return graph


def load_game_relations(graph, path='./output/', debug=False):
    with open(path + 'user_game_rels.csv', 'r') as f:
        csv_reader = csv.reader(f, delimiter=',')
        
        for relation in csv_reader:
            if (relation[0] in graph and relation[1] in graph):
                graph.add_edge(relation[0], relation[1])
            else:
                if (debug):
                    if (not(relation[0] in graph)):
                        print('WARNING: USER %s not exist' % relation[0])
                    if (not(relation[1] in graph)):
                        print('WARNING: GAME %s not exist' % relation[1])
    
    return graph

if __name__ == "__main__":
       
    g = nx.Graph()
    g = load_users(g, debug=True)
    g = load_user_relations(g)
    g = load_games(g)
    g = load_game_relations(g)
    

    
