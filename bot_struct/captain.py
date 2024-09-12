"""Module to define the struct of Captain"""

from discord import Embed, Member
from config import DEFAULT_BALANCE, DEFAULT_PRICE, TEAM_SIZE


class Captain:
    """Class as the struct of Captain"""

    member: list[int]
    balance: int
    owner: Member

    def __init__(self, owner: Member) -> None:
        self.member = []
        self.balance = DEFAULT_BALANCE
        self.owner = owner

    def available_balance(self) -> int:
        """Function to get current usable balabce per captain"""
        # 限制叫價唔可以 > 剩餘位置 * 底價
        return self.balance - self.remain_slot() * DEFAULT_PRICE

    def is_full(self) -> bool:
        """
        Check the team full or not

        每隊有指定人數限制 (不能多不能少)
        """
        return len(self.member) >= (TEAM_SIZE - 1)

    def remain_slot(self) -> int:
        """
        How many slot left till full

        Team size - self - bought members
        """
        return TEAM_SIZE - 1 - len(self.member)

    def gen_embed(self) -> Embed:
        """
        Generate embed object of Captain
        """
        embed = Embed(
            title="Self statistic",
            description=f"Balance: {self.balance} members: {len(self.member)}/{TEAM_SIZE - 1}",
        )

        embed.add_field(name="Members", inline=False, value=",".join(self.member))
        embed.add_field(
            name="Usable balance", inline=True, value=self.available_balance()
        )
        return embed
