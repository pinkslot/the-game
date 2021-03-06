from controller.basic_controller import BasicController
from stdnet import odm
from stdnet.utils.exceptions import CommitException, ObjectNotFound
from game_exception import *
from common import jsonify

class GameController(BasicController):
    """Controller for all actions with games"""

    def __init__(self, json, models, games):
        super(GameController, self).__init__(json, models.user)
        self.games = models.game
        self.maps = models.map
        self.current_games = games

    def create_game(self):
        if self.user.game:
            raise AlreadyInGame()

        try:
            map = self.maps.get(id=int(self.json['map']))
        except (ValueError, ObjectNotFound):
            raise BadMap()

        try:
            game = self.games.new(map = map, name =  str(self.json['name']), max_players = int(str(self.json['maxPlayers'])))
            self.user.game = game
            self.user.save()
            self.current_games.add_game(game.id, map.map, self.json.get('consts')) #.add_player(self.user.id, self.user.login)
        except CommitException:
            raise GameExists()
        except ValueError:
            raise BadMaxPlayers()
        return jsonify(result="ok")

    def get_stats(self):
        gameid = int(self.json["game"])
        try:
            game = self.games.get(gameid)
            if game.status == "running":
                raise BadGame()
        except:
            raise BadGame()

        return jsonify(
            players=[{
                login: player.login,
                kills: player.kills,
                deaths: player.deaths
            } for player in game.player_stats]
        )

    def get_games(self):
        games = self.games.filter(status=str(self.json["status"])).all() if self.json.get("status") else self.games.all()

        return jsonify(
            games=[{
                "name": game.name,
                "id": game.id,
                "map": game.map.id,
                "maxPlayers": game.max_players,
                "players": [player.login for player in game.players.all()],
                "status": game.status
                } for game in games],
            result="ok")
