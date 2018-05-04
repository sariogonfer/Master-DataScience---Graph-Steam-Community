from queue import Full, Queue
import os
import signal
import time

import json

import requests

SEED_STEAMID = '76561198083091304'

API_KEY = "71C140A947501AB3DFE96076DF4951D8"

SERVER_ENDPOINT = "http://api.steampowered.com"
PLAYER_ENDPOINT = lambda steamid: ("{}/ISteamUser/GetPlayerSummaries/v0002/"
                                   "?key={}&steamids={}".format(
                                       SERVER_ENDPOINT, API_KEY, steamid))
FRIENDS_ENDPOINT = lambda steamid: ("{}/ISteamUser/GetFriendList/v0001/?key={}"
                                    "&steamid={}".format(SERVER_ENDPOINT,
                                                          API_KEY, steamid))
OWNED_GAMES = lambda steamid: ("{}/IPlayerService/GetOwnedGames/v0001/?key={}"
                               "&steamid={}&include_appinfo=1"
                               "&include_played_free_games=1".format(
                                   SERVER_ENDPOINT, API_KEY, steamid))
PROCESSED_STEAMIDS = set()
PROCESSED_GAMEIDS = set()
STEAMID_QUEUE = Queue(maxsize=1000)


def get_summary(steamids):
    s = ",".join(steamids)
    response = requests.get(PLAYER_ENDPOINT(steamids))

    return response.json()

def get_friends(steamid):
    response = requests.get(FRIENDS_ENDPOINT(steamid))

    return response.json()

def get_owned_games(steamid):
    response = requests.get(OWNED_GAMES(steamid))

    return response.json()

class DataSaver:
    path = None
    f_users = None
    f_games = None
    f_user_user_rels = None
    f_user_game_rels = None
    f_processed_steamids = None
    f_processed_gameids = None

    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.f_users= open(os.path.join(self.path, 'user.json'), 'w')
        self.f_games = open(os.path.join(self.path, 'games.json'), 'w')
        self.f_user_user_rels = open(os.path.join(self.path,
                                     'user_user_rels.csv'), 'w')
        self.f_user_game_rels = open(os.path.join(self.path,
                                     'user_game_rels.csv'), 'w')

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.f_users.close()
        self.f_games.close()
        self.f_user_user_rels.close()
        self.f_user_game_rels.close()
        self.save_processed_queues()
        self.save_pending_queue()

    def save_pending_queue(self):
        with open(os.path.join(self.path, 'pendding.csv'), 'w') as f_queue:
            while not  STEAMID_QUEUE.empty():
                print(STEAMID_QUEUE.get(), file=f_queue)

    def save_processed_queues(self):
        with open(os.path.join(self.path, 'processed_steamids.csv'), 'w') as \
                f_processed_steamids:
            for id_ in PROCESSED_STEAMIDS:
                print(id_, file=f_processed_steamids)
        with open(os.path.join(self.path, 'processed_gameids.csv'), 'w') as \
                f_processed_gameids:
            for id_ in PROCESSED_STEAMIDS:
                print(id_, file=f_processed_gameids)

    def save_user(self, data):
        print(data, file=self.f_users)

    def save_games(self, data):
        for g in data:
            print(json.dumps(g), file=self.f_games)

    def save_user_user_rels(self, relations):
        for u1, u2 in relations:
            print('{},{}'.format(u1, u2), file=self.f_user_user_rels)

    def save_user_game_rels(self, relations):
        for u, g, t in relations:
            print('{},{},{}'.format(u, g, t), file=self.f_user_game_rels)


class SteamUser:
    _steamid = None
    _summary = None
    _friends = None
    _owned_games = None
    def __init__(self, steamid):
        self._steamid = steamid

    @property
    def friends(self):
        if not self._friends:
            self._friends = get_friends(self._steamid)
        return self._friends

    @property
    def owned_games(self):
        if not self._owned_games:
            self._owned_games = get_owned_games(self._steamid)
        return self._owned_games

    @property
    def summary(self):
        if not self._summary:
            self._summary = get_summary(self._steamid)
        return self._summary

    @property
    def friend_ids(self):
        friend_list = self.friends.get('friendslist', {})
        return [f['steamid'] for f in friend_list.get('friends', [])]

    @property
    def owned_games_ids(self):
        return [g['appid'] for g in self.owned_games['response'] \
                .get('games', [])]

    @property
    def owned_games_playtime(self):
        return [(g['appid'], g['playtime_forever']) for g in \
                self.owned_games['response'].get('games', [])]

    def get_friend_rels(self, exclude=[]):
        for friend_id in [f for f in self.friend_ids if not f in exclude]:
            yield self._steamid, friend_id

    def get_game_rels(self):
        for game in self.owned_games_playtime:
            yield self._steamid, game[0], game[1]

    def get_owned_games_info(self, exclude=[]):
        return [g for g in self.owned_games['response'].get('games', []) \
                if not g['appid'] in exclude]


def process_steamid(steamid, saver):
    yo = SteamUser(steamid)
    saver.save_user(json.dumps(yo.summary))
    saver.save_user_user_rels(yo.get_friend_rels(PROCESSED_STEAMIDS))
    saver.save_user_game_rels(yo.get_game_rels())
    saver.save_games(yo.get_owned_games_info(exclude=PROCESSED_GAMEIDS))
    PROCESSED_GAMEIDS.update(yo.owned_games_ids)
    PROCESSED_STEAMIDS.add(steamid)

    return yo.friend_ids


stop = False


def signal_handler(signal, frame):
    global stop
    stop = True


signal.signal(signal.SIGINT, signal_handler)


def harvest_info(seed_steamid):
    STEAMID_QUEUE.put(seed_steamid)
    with DataSaver('./output') as saver:
        while not STEAMID_QUEUE.empty() and not stop:
            try:
                steamid = STEAMID_QUEUE.get()
                if steamid in PROCESSED_STEAMIDS:
                    continue
                friend_ids = process_steamid(steamid, saver)
                for si in [id_ for id_ in friend_ids \
                           if not id_ in PROCESSED_STEAMIDS]:
                    try:
                        STEAMID_QUEUE.put(si, block=False)
                    except Full:
                        break
                time.sleep(0.1)
            except Exception as e:
                print(e)
                print('Failed. ID: {}'.format(steamid))

if __name__ == "__main__":
    harvest_info(SEED_STEAMID)
