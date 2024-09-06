import asyncio, random

from data.item import Item

TICK_INTERVAL = 0.5

class Auction:
    item: Item | None
    players: list[Item]
    pass_players: list[Item]
    pause: bool

    def __init__(self, players: list[Item]) -> None:
        self.item = players.pop(0)
        self.players = players
        self.pass_players = []
        self.pause = False

    def is_finished(self) -> bool:
        return True

    def is_pause(self) -> bool:
        return self.pause

    def swap_pass_player(self):
        self.players = self.pass_players
        self.pass_players = []

    def random_pop(self) -> Item | None:
        return (
            self.players.pop(random.randint(0, self.players.__len__() - 1))
            if self.players.__len__() > 0
            else None
        )

    async def tick(self):
        if self.item is None:
            return

        if not self.item.is_expiry():
            return

        if self.item.is_pass():
            self.pass_players.append(self.item)
        else:
            # Handle item transition to owner
            self.item.owner.member.append(self.item.uid)
            self.item.owner.balance -= self.item.price

        self.item = self.players.pop(0)


async def background_auction(auction: Auction):
    while not auction.is_finished():
        await auction.tick()
        await asyncio.sleep(TICK_INTERVAL)
