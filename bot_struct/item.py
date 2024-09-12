import time
from bot_struct.captain import Captain
from config import (
    AFTER_BID_WAIT,
    DEFAULT_PRICE,
    FIRST_TIME_WAIT,
)


class Item:
    player_id: int
    price: int
    expiry: int
    owner: Captain | None
    
    def __init__(self, uid: int) -> None:
        self.player_id = uid
        self.price = DEFAULT_PRICE
        self.owner = None
        
        self.expiry = int(time.time()) + FIRST_TIME_WAIT

    def set_owner(self, price: int, owner: Captain):
        self.price = price
        self.owner = owner
        
        # Update
        self.expiry = int(time.time()) + AFTER_BID_WAIT

    def is_unsold(self) -> bool:
        return self.owner is None

    def is_expiry(self) -> bool:
        return int(time.time()) > self.expiry

    def generate_embed(self):
        pass
