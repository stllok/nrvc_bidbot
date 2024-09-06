import time

from discord import Member

from data.captain import Captain
from config import (
    AFTER_BID_WAIT,
    DEFAULT_PRICE,
    FIRST_TIME_WAIT,
)


class Item:
    uid: int
    price: int
    owner: Captain | None
    expiry: int
    owner: Member
    
    def __init__(self, uid: int, owner: Member) -> None:
        self.uid = uid
        self.price = DEFAULT_PRICE
        self.owner = None
        self.expiry = int(time.time()) + FIRST_TIME_WAIT
        self.owner = owner

    def set_owner(self, price: int, owner: Captain):
        self.price = price
        self.expiry = int(time.time()) + AFTER_BID_WAIT
        self.owner = owner

    def is_pass(self) -> bool:
        return self.owner is None

    def is_expiry(self) -> bool:
        return int(time.time()) > self.expiry

    def print_msg(self):
        pass
