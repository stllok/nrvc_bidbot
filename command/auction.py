import random
import discord
from discord import Member, User, app_commands
from discord.ext import commands, tasks

from bot import NRVCBot
from config import MINIMUM_CALL_PRICE, MY_GUILD_ID_OBJECT
from data.captain import Captain
from data.item import Item


# 定義名為 Ping 的 Cog
class Auction(commands.Cog):
    bot: commands.Bot
        # List
    players: list[Item]
    pass_players: list[Item]
    captains: list[Captain]
        # Status
    item: Item | None
    pause = False

    def __init__(self, bot: NRVCBot, players: list[Item], captains: list[Captain]):
        self.bot = bot
        # List
        self.players = players
        self.captains = captains
        self.pass_players = []
        # Status
        self.item = None
        self.pause = False

    def random_pop(self) -> Item | None:
        return (
            self.players.pop(random.randint(0, self.players.__len__() - 1))
            if self.players.__len__() > 0
            else None
        )
        
    def get_captains(self, user: User | Member) -> Captain | None:
        for captain in self.captains:
            if captain.owner.id == user.id:
                return captain
        
        return None
        
    @app_commands.command(name="start-auction", description="Start the auction")
    @app_commands.guilds(MY_GUILD_ID_OBJECT)
    async def start(self, interaction: discord.Interaction):
        self.players = self.pass_players
        self.pass_players = []
        await interaction.response.send_message("Swapped list")
        
    @app_commands.command(name="swap-pass-player", description="Start the auction")
    @app_commands.guilds(MY_GUILD_ID_OBJECT)
    async def swap_pass_player(self, interaction: discord.Interaction):
        self.players = self.pass_players
        self.pass_players = []
    
    @app_commands.command(name="bid-min", description=f"Bid with the minimum amount ({MINIMUM_CALL_PRICE})")
    @app_commands.guilds(MY_GUILD_ID_OBJECT)
    async def bid_min(self, interaction: discord.Interaction):
        captain = self.get_captains(interaction.user)
        
        if captain is None:
            await interaction.response.send_message("You are not captain", ephemeral=True)
            return
        
        if self.item is None:
            await interaction.response.send_message("Item not exists", ephemeral=True)
            return
                
        self.item.set_owner(MINIMUM_CALL_PRICE, captain)
        await interaction.response.send_message("Success", ephemeral=True)
        
    
    @app_commands.command(name="bid", description="Bid with the specific amount")
    @app_commands.guilds(MY_GUILD_ID_OBJECT)
    async def bid(self, interaction: discord.Interaction, amount: int):
        captain = self.get_captains(interaction.user)
        
        if captain is None:
            await interaction.response.send_message("You are not captain", ephemeral=True)
            return
        
        if self.item is None:
            await interaction.response.send_message("Item not exist", ephemeral=True)
            return
        
        if amount < self.item.price + MINIMUM_CALL_PRICE:
            await interaction.response.send_message(f"Invalid price (current price: {self.item.price}; valid call: {self.item.price + MINIMUM_CALL_PRICE})", ephemeral=True)
            return
                
        self.item.set_owner(MINIMUM_CALL_PRICE, captain)
        await interaction.response.send_message("Success", ephemeral=True)

    @tasks.loop(seconds=0.5)
    async def tick(self):
        if self.item is None or self.pause:
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
        
        
        
    @tick.before_loop
    async def before_task(self):
        self.item = self.random_pop()

