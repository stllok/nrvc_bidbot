from discord import Member
import json
from bot_struct.captain import Captain
from bot_struct.item import Item


class Bidded:
    player_id: int
    owner: str
    price: int

    def __init__(self, player_id: int, price: int, owner: str):
        self.player_id = player_id
        self.price = price
        self.owner = owner

    def restore(self, captains: list[Captain], players: list[Item]):
        captain = next(
            iter(filter(lambda captain: captain.owner.name == self.owner, captains)),
            None,
        )
        player = next(
            iter(filter(lambda player: player.player_id == self.player_id, players)),
            None,
        )

        if captain is None:
            raise Exception("Captain not found")
        if player is None:
            raise Exception("Player not found")
        print(
            f"Restoring record of {captain.owner.name} bought {player.player_name} with price {self.price}"
        )
        captain.balance -= self.price
        captain.member.append(self.player_id)
        players.remove(player)

    def __jsonencode__(self):
        return {"player_id": self.player_id, "price": self.price, "owner": self.owner}


FILE_PATH = "history.json"


class AdvancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "__jsonencode__"):
            return obj.__jsonencode__()

        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class ActionHistory:
    history: list[Bidded]

    def __init__(self) -> None:
        self.history = []

        try:
            with open(FILE_PATH, "r") as f:
                self.history = list(
                    map(
                        lambda j: Bidded(j["player_id"], j["price"], j["owner"]),
                        json.loads(f.read()),
                    )
                )
        except FileNotFoundError:
            print(f"{FILE_PATH} not found, creating new one")
            self.sync()

        print(f"Loaded {len(self.history)} record")

    def sync(self):
        with open(FILE_PATH, "w") as f:
            json.dump(self.history, f, cls=AdvancedJSONEncoder)

    def push(self, player_id: int, price: int, owner: Member):
        self.history.append(Bidded(player_id, price, owner.name))
        self.sync()

    def restore(self, captains: list[Captain], players: list[Item]):
        for h in self.history:
            h.restore(captains, players)
