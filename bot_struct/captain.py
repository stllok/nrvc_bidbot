from discord import Member
from config import DEFAULT_BALANCE, DEFAULT_PRICE, TEAM_SIZE

class Captain:
    member: list[int]
    balance: int
    owner: Member
    
    def __init__(self, owner: Member) -> None:
        self.member = []
        self.balance = DEFAULT_BALANCE
        self.owner = owner

    def available_balance(self) -> int:
        # 限制叫價唔可以 > 剩餘位置 * 底價
        return self.balance - self.remain_slot() * DEFAULT_PRICE

    def is_full(self) -> bool:
        # 每隊有指定人數限制 (不能多不能少)
        return self.member.__len__() >= (TEAM_SIZE - 1)
    
    def remain_slot(self) -> int:
        # TS - self - bought members
        return TEAM_SIZE - 1 - self.member.__len__()
