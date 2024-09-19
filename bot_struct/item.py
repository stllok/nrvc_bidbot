import time

from discord import Embed
from bot_struct.captain import Captain
from config import (
    AFTER_BID_WAIT,
    FIRST_TIME_WAIT,
)


class Item:
    # Player info
    player_id: int
    player_name: str
    # Player qualify and skill data
    sip: int
    etx: float
    seed: int
    # Auction data
    price: int
    expiry: int
    owner: Captain | None
    
    def __init__(self, uid: int, sip: int, etx: float, seed: int, name: str) -> None:
        self.player_id = uid
        self.sip = sip
        self.etx = etx
        self.seed = seed
        self.player_name = name

        self.price = 0
        self.owner = None

    def set_owner(self, price: int, owner: Captain):
        self.price = price
        self.owner = owner
        # Update
        self.expiry = int(time.time()) + AFTER_BID_WAIT
    
    def init_expiry(self):
        self.expiry = int(time.time()) + FIRST_TIME_WAIT

    def is_unsold(self) -> bool:
        return self.owner is None

    def is_expiry(self) -> bool:
        return int(time.time()) > self.expiry

    def generate_embed(self) -> Embed:
        embed = Embed(
            title=f"🪪Bidding ({self.player_name})",
            url=f"https://osu.ppy.sh/users/{self.player_id}",
        )
        embed.add_field(name="🕒Expiry in", value=f"<t:{self.expiry}:R>")
        embed.add_field(name="💵Price", value=self.price)
        embed.add_field(name="📃Qualify Seed", value=self.seed)
        embed.add_field(name="📊ETX Rating", value=self.etx)
        embed.add_field(name="📊Skill Issue Rating", value=self.sip)
        embed.add_field(name="🙋‍♂️Current Caller", value=self.owner.owner.name if self.owner is not None else None)
        embed.set_image(url=f"https://a.ppy.sh/{self.player_id}")
        embed.set_footer(
            text="👉Use `/bid` or `/bid-min` or below button shortcut to call price!"
        )
        return embed

    def __str__(self) -> str:
        return self.player_name