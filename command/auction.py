from optparse import Option
import random, asyncio
import time
import discord
from discord import Member, TextChannel, User, app_commands
from discord.ext import commands, tasks

from config import BEFORE_BID_START_WAIT, MINIMUM_CALL_PRICE, MY_GUILD_ID_OBJECT
from bot_struct.captain import Captain
from bot_struct.item import Item


# 定義名為 Ping 的 Cog
class Auction(commands.Cog):
    bot: commands.Bot
    # List
    players: list[Item]
    unsold_players: list[Item]
    captains: list[Captain]
    # Status
    item: Item | None
    # Bidding Channel
    interactive_channel:TextChannel | None
    # Timestamp based pause
    pause_timestamp = Option[int]

    def __init__(self, bot: commands.Bot, players: list[Item], captains: list[Captain]):
        self.bot = bot
        # List
        self.players = players
        self.captains = captains
        self.unsold_players = []
        # Status
        self.item = None
        self.pause_timestamp = None
        self.interactive_channel = None

    def random_pop(self) -> Item | None:
        return (
            self.players.pop(random.randint(0, self.players.__len__() - 1))
            if self.players.__len__() > 0
            else None
        )

    def get_captains(self, user: User | Member) -> Captain | None:
        return next(
            iter(filter(lambda captain: captain.owner.id == user.id, self.captains)),
            None,
        )

    def broadcast_embed(self):
        raise Exception("TODO")

    async def bid_action(self, interaction: discord.Interaction, amount: int):
        captain = self.get_captains(interaction.user)

        if captain is None:
            await interaction.response.send_message(
                "You are not captain", ephemeral=True
            )
            return

        if self.item is None:
            await interaction.response.send_message(
                "Item not exists yet", ephemeral=True
            )
            return

        if amount < self.item.price + MINIMUM_CALL_PRICE:
            await interaction.response.send_message(
                f"Invalid price (current price: {self.item.price}; valid call: {self.item.price + MINIMUM_CALL_PRICE})",
                ephemeral=True,
            )
            return

        self.item.set_owner(MINIMUM_CALL_PRICE, captain)
        await interaction.response.send_message("Success", ephemeral=True)

    @app_commands.command(name="start-auction", description="Start the auction")
    @app_commands.guilds(MY_GUILD_ID_OBJECT)
    async def start(self, interaction: discord.Interaction):
        self.players = self.unsold_players
        self.interactive_channel = interaction.channel
        self.unsold_players = []
        await interaction.response.send_message("Swapped list")

    @app_commands.command(name="swap-unsold-player", description="Start the auction")
    @app_commands.guilds(MY_GUILD_ID_OBJECT)
    async def swap_unsold_player(self, interaction: discord.Interaction):
        self.players = self.unsold_players
        self.unsold_players = []

    @app_commands.command(
        name="bid-min",
        description=f"Bid with the minimum amount ({MINIMUM_CALL_PRICE})",
    )
    @app_commands.guilds(MY_GUILD_ID_OBJECT)
    async def bid_min(self, interaction: discord.Interaction):
        await self.bid_action(interaction, MINIMUM_CALL_PRICE)

    @app_commands.command(name="bid", description="Bid with the specific amount")
    @app_commands.guilds(MY_GUILD_ID_OBJECT)
    async def bid(self, interaction: discord.Interaction, amount: int):
        await self.bid_action(interaction, amount)

    @tasks.loop(seconds=0.2)
    async def on_bidding(self):
        if (
            self.item is None  # Item not exists
            or self.pause_timestamp is not None  # Paused
            or not self.item.is_expiry()  # Item not expiry yet
        ):
            return

        if self.item.is_unsold():
            self.unsold_players.append(self.item)
        else:
            # Handle item transition to owner
            self.item.owner.member.append(self.item.player_id)
            self.item.owner.balance -= self.item.price

        # Reset everything to start
        self.on_bidding.restart()

    @on_bidding.before_loop
    async def pre_bidding(self):
        item = self.random_pop()
        
        if item is None:
            self.on_bidding.stop()
        else:
            self.item = item
        
        self.interactive_channel.send(f"The next auction will be started in <t:{int(time.time()) + BEFORE_BID_START_WAIT}:R>")
        await asyncio.sleep(BEFORE_BID_START_WAIT)
        await self.bot.wait_until_ready()
        
    @on_bidding.after_loop
    async def post_bidding(self):
        # Status reset
        self.item = None
