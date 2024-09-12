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
    interactive_channel: TextChannel | None

    def __init__(self, bot: commands.Bot, players: list[Item], captains: list[Captain]):
        self.bot = bot
        # List
        self.players = players
        self.captains = captains
        self.unsold_players = []
        # Status
        self.item = None
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

    async def broadcast_embed(self):
        embed = discord.Embed(
            title="Bidding (stllok)",
            url=f"https://osu.ppy.sh/users/{self.item.player_id}",
            description=f"In-Queue: {len(self.players)}\tUnsold: {len(self.unsold_players)}",
        )
        embed.add_field(name="Expiry in", value=f"<t:{self.item.expiry}:R>")
        embed.add_field(name="Price", value=self.item.price)
        embed.add_field(name="Qualify Seed", value="WIP")
        embed.add_field(name="ETX Rating", value="WIP")
        embed.add_field(name="Skill Issue Rating", value="WIP")
        embed.add_field(name="Current Caller", value=self.item.owner)
        embed.set_image(url=f"https://a.ppy.sh/{self.item.player_id}")
        embed.set_footer(
            text="Use `/bid` or `/bid-min` or below button shortcut to call price!"
        )

        buttons_settings = [
            [f"Minimum (+{MINIMUM_CALL_PRICE})", self.bid_min],
            ["+50", lambda interact: self.bid(interact, 50)],
            ["+100", lambda interact: self.bid(interact, 100)],
            ["+250", lambda interact: self.bid(interact, 250)],
            ["+500", lambda interact: self.bid(interact, 500)],
        ]

        view = discord.ui.View()
        for button_settings in buttons_settings:
            button = discord.ui.Button(label=button_settings[0])
            button.callback = button_settings[1]
            view.add_item(item=button)

        await self.interactive_channel.send(view=view, embed=embed)

    async def bid_action(self, interaction: discord.Interaction, amount: int):
        captain = self.get_captains(interaction.user)

        conditions = [
            (lambda: captain is None, "You are not the captain"),
            (lambda: self.item is None, "Auction is not ready yet"),
            (
                lambda: amount > captain.available_balance(),
                f"You don't have enough balance! (Available: {captain.available_balance()})",
            ),
            (
                lambda: amount < self.item.price + MINIMUM_CALL_PRICE,
                f"Invalid price (current price: {self.item.price}; valid call: {self.item.price + MINIMUM_CALL_PRICE})",
            ),
            (
                captain.is_full,
                "Your team is full!",
            ),
        ]

        for condition in conditions:
            if condition[0]():
                return await interaction.response.send_message(
                    condition[1], ephemeral=True
                )

        self.interactive_channel.send(
            f"{interaction.user.name} has called {amount}! ({self.item.price} => {amount})"
        )
        self.item.set_owner(MINIMUM_CALL_PRICE, captain)
        await self.broadcast_embed()

        await interaction.response.send_message("Success", ephemeral=True)

    @app_commands.command(name="start-auction", description="Start the auction")
    @app_commands.guilds(MY_GUILD_ID_OBJECT)
    async def start(self, interaction: discord.Interaction):
        self.interactive_channel = interaction.channel
        await interaction.response.send_message("Starting auction")
        self.on_bidding.start()

    @app_commands.command(name="swap-unsold-player", description="Start the auction")
    @app_commands.guilds(MY_GUILD_ID_OBJECT)
    async def swap_unsold_player(self, interaction: discord.Interaction):
        if self.unsold_players.__len__() == 0:
            return await interaction.response.send_message("Unsold list is empty!! nothing change", ephemeral=True)
        
        self.players = self.unsold_players
        self.unsold_players = []
        await interaction.response.send_message("Swapped list", ephemeral=True)

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

    #######################
    # EPHEMERAL FUNCTION  #
    #######################

    #######################
    # ADMIN ONLY FUNCTION #
    #######################
    @app_commands.command(name="cancel", description="Start the auction")
    @app_commands.guilds(MY_GUILD_ID_OBJECT)
    async def cancel(self, interaction: discord.Interaction):
        self.on_bidding.stop()

    #######################
    #   BACKGROUND TASK   #
    #######################
    @tasks.loop(seconds=0.2)
    async def on_bidding(self):
        if (
            self.item is None  # Item not exists
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
            # Stop bid when nothing left
            self.interactive_channel.send("Auction ended")
            self.on_bidding.stop()
        else:
            self.item = item

        self.interactive_channel.send(
            f"The next auction will be started in <t:{int(time.time()) + BEFORE_BID_START_WAIT}:R>"
        )
        await asyncio.sleep(BEFORE_BID_START_WAIT)
        await self.bot.wait_until_ready()

    @on_bidding.after_loop
    async def post_bidding(self):
        # Status reset
        self.item = None