import requests


class Globals:
    def __init__(self, player):
        self.name = player['name']
        self.platform = player['platform']
        self.level = player['level']
        self.mm_rankScore = player['rank']['rankScore']
        self.mm_rankName = player['rank']['rankName']
        self.mm_rankDiv = player['rank']['rankDiv']
        self.mm_rankImg = player['rank']['rankImg']
        self.mm_rankAsText = f'{self.mm_rankName} {self.mm_rankDiv}'
        self.ar_rankScore = player['arena']['rankScore']
        self.ar_rankName = player['arena']['rankName']
        self.ar_rankDiv = player['arena']['rankDiv']
        self.ar_rankAsText = f'{self.ar_rankName} {self.ar_rankDiv}'
        self.ar_rankImg = player['arena']['rankImg']


class RealTime:
    def __init__(self, player):
        self.lobbyState = player['lobbyState']
        self.currentState = player['currentStateAsText']


class Player:
    def __init__(self, json):
        self.json = json
        self.global_player = Globals(self.json['global'])
        self.realtime_player = RealTime(self.json['realtime'])


class API:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def make_request(self, params):
        return requests.get(url='https://api.mozambiquehe.re/bridge?version=5', params=params).json()

    def get_player(self, name: str, platform: str):
        req = self.make_request(params={'platform': platform, 'player': name, 'auth': self.api_key})
        try:
            temp = req['global']
        except KeyError or AttributeError:
            return None
        return Player(req)

