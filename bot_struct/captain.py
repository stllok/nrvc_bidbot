"""Module to define the struct of Captain"""

from discord import Embed, Member
from config import DEFAULT_BALANCE, DEFAULT_PRICE, PLAYERS, TEAM_SIZE


class Captain:
    """Class as the struct of Captain"""

    member: list[int]
    balance: int
    owner: Member

    def __init__(self, owner: Member) -> None:
        self.member = []
        self.balance = DEFAULT_BALANCE
        self.owner = owner

    def member_to_string(self) -> list[str]:
        return list(
            map(
                lambda p: f"`{p["name"]}`",
                filter(lambda p: p["player_id"] in self.member, PLAYERS),
            )
        )

    def available_balance(self) -> int:
        """Function to get current usable balabce per captain"""
        # 1600, 1700, 1800, 1900, 2000 for 0, 1, 2, 3, 4, 5 players in captain's team
        return self.balance - (self.remain_slot() + 1) * DEFAULT_PRICE 

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
            description=f"💰Balance: {self.balance} 🏃Members: {len(self.member)}/{TEAM_SIZE - 1}",
        )

        embed.add_field(name="🧍‍♂️Members", inline=False, value=",".join(self.member_to_string()))
        embed.add_field(
            name="💳Usable balance", inline=True, value=self.available_balance()
        )
        return embed

    def __str__(self) -> str:
        return f"{self.owner.name} ({self.balance})"
