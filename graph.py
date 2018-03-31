import networkx as nx
import json
import csv 


def load_users(graph, path='./output/'):
    with open(path + 'user_copy.json', 'r') as f:
        for user in f:
            try:
                user_json = json.loads(user)
                player = user_json['response']['players'][0]
                
                #Creating a new node
                graph.add_node(player['steamid'],
                    type            ='user',
                    profileurl      = player['profileurl'],
                    realname        = player['realname'],
                    loccountrycode  = player['loccountrycode'],
                    avatar          = {
                                        player['avatar'],
                                        player['avatarmedium'],
                                        player['avatarfull']
                                      },
                    timecreated     = player['timecreated'],
                    lastlogoff      = player['lastlogoff'],
                    personaname     = player['personaname'])
                    
            except ValueError:
                print ('ERROR Decoding USER json failed')
    
    return graph


def load_user_relations(graph, path='./output/'):
    with open(path + 'user_user_rels.csv', 'r') as f:
        csv_reader = csv.reader(f, delimiter=',')
        
        for relation in csv_reader:
            if (relation[0] in graph and relation[1] in graph):
                graph.add_edge(relation[0], relation[1])
            else:
                if (not(relation[0] in graph)):
                    print('WARNING: USER %s not exist' % relation[0])
                if (not(relation[1] in graph)):
                    print('WARNING: USER %s not exist' % relation[1])
    
    return graph

def load_games(graph, path='./output/'):
    with open(path + 'games.json', 'r') as f:
        for game_f in f:
            try:
                game = json.loads(game_f)
                
                #Creating a new node
                graph.add_node(game['appid'],
                    type                        ='game',
                    name                        = game['name'],
                    img_icon_url                = game['img_icon_url'],
                    img_logo_url                = game['img_logo_url'],
                    has_community_visible_stats = game['has_community_visible_stats'] if 'has_community_visible_stats' in game else False)
                    
            except ValueError:
                print ('ERROR Decoding GAME json failed')
    
    return graph


def load_game_relations(graph, path='./output/'):
    with open(path + 'user_game_rels.csv', 'r') as f:
        csv_reader = csv.reader(f, delimiter=',')
        
        for relation in csv_reader:
            if (relation[0] in graph and relation[1] in graph):
                graph.add_edge(relation[0], relation[1])
            else:
                if (not(relation[0] in graph)):
                    print('WARNING: USER %s not exist' % relation[0])
                if (not(relation[1] in graph)):
                    print('WARNING: GAME %s not exist' % relation[1])
    
    return graph

if __name__ == "__main__":
       
    g = nx.Graph()
    g = load_users(g)
    g = load_user_relations(g)
    g = load_games(g)
    g = load_game_relations(g)
    

    
