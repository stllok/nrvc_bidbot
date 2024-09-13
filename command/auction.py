import random
import asyncio
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
        if self.item is None:
            print("NO ITEM TO BROADCAST!!!")
            return

        embed = self.item.generate_embed()
        # embed.description = (
        #     f"In-Queue: {len(self.players)}\tUnsold: {len(self.unsold_players)}",
        # )

        buttons_settings = [
            [f"Minimum (+{MINIMUM_CALL_PRICE})", lambda interaction: self.bid_action(interaction, MINIMUM_CALL_PRICE + self.item.price)],
            ["+50", lambda interact: self.bid_action(interact, 50 + self.item.price)],
            ["+100", lambda interact: self.bid_action(interact, 100 + self.item.price)],
            ["+250", lambda interact: self.bid_action(interact, 250 + self.item.price)],
            ["+500", lambda interact: self.bid_action(interact, 500 + self.item.price)],
        ]

        view = discord.ui.View()
        for button_setting in buttons_settings:
            button = discord.ui.Button(label=button_setting[0])
            button.callback = button_setting[1]
            view.add_item(item=button)

        modal_custom_bid = CustomBidMoral()
        modal_custom_bid.set_auction(self)

        btn_custom_bid = discord.ui.Button(label="Custom Bid")
        btn_custom_bid.callback = lambda interact: interact.response.send_modal(
            modal_custom_bid
        )

        view.add_item(item=btn_custom_bid)

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

        await self.interactive_channel.send(
            f"{interaction.user.name} has called {amount}! ({self.item.price} => {amount})"
        )
        self.item.set_owner(amount, captain)
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
            return await interaction.response.send_message(
                "Unsold list is empty!! nothing change", ephemeral=True
            )

        self.players = self.unsold_players
        self.unsold_players = []
        await interaction.response.send_message("Swapped list", ephemeral=True)

    @app_commands.command(
        name="bid-min",
        description=f"Bid with the minimum amount ({MINIMUM_CALL_PRICE})",
    )
    @app_commands.guilds(MY_GUILD_ID_OBJECT)
    async def bid_min(self, interaction: discord.Interaction):
        await self.bid_action(interaction, MINIMUM_CALL_PRICE + self.item.price)

    @app_commands.command(name="bid", description="Bid with the specific amount")
    @app_commands.guilds(MY_GUILD_ID_OBJECT)
    async def bid(self, interaction: discord.Interaction, amount: int):
        await self.bid_action(interaction, amount)

    #######################
    # EPHEMERAL FUNCTION  #
    #######################

    @app_commands.command(name="statme", description="Get your status")
    @app_commands.guilds(MY_GUILD_ID_OBJECT)
    async def statme(self, interaction: discord.Interaction):
        captain = self.get_captains(interaction.user)

        if captain is None:
            return await interaction.response.send_message(
                "You are not captain", ephemeral=True
            )

        await interaction.response.send_message(
            embed=captain.gen_embed(), ephemeral=True
        )

    #######################
    # ADMIN ONLY FUNCTION #
    #######################
    @app_commands.command(name="cancel", description="Cancel current auction")
    @app_commands.guilds(MY_GUILD_ID_OBJECT)
    @commands.has_permissions(administrator=True)
    async def cancel(self, interaction: discord.Interaction):
        self.on_bidding.stop()

    @app_commands.command(
        name="modify_balance", description="Modify specific captain's balance"
    )
    @app_commands.guilds(MY_GUILD_ID_OBJECT)
    @commands.has_permissions(administrator=True)
    async def modify_balance(
        self, interaction: discord.Interaction, req_captain: Member, amount: int
    ):
        captain = self.get_captains(req_captain)

        if captain is None:
            return await interaction.response.send_message(
                "You are not captain", ephemeral=True
            )

        captain.balance = amount
        await interaction.response.send_message(
            f"Adjusted {captain.owner} balance to {amount}", ephemeral=True
        )

    @app_commands.command(name="captains-status", description="Get all captains status")
    @app_commands.guilds(MY_GUILD_ID_OBJECT)
    async def captains_status(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            content="\n".join(
                map(
                    lambda captain: f"{captain.owner} (${captain.balance}): {','.join(captain.member)}",
                    self.captains,
                )
            ),
            ephemeral=True,
        )

    @app_commands.command(name="bid-status", description="Get all captains status")
    @app_commands.guilds(MY_GUILD_ID_OBJECT)
    @commands.has_permissions(administrator=True)
    async def bid_status(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"""
            On queue({len(self.players)}): {", ".join(map(lambda player: player.player_name ,self.players))}
            Unsold({len(self.unsold_players)}): {", ".join(map(lambda player: player.player_name ,self.unsold_players))}
            """,
            ephemeral=True,
        )

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

        await self.interactive_channel.send(
            f"The next auction will be started in <t:{int(time.time()) + BEFORE_BID_START_WAIT}:R>"
        )
        await asyncio.sleep(BEFORE_BID_START_WAIT)
        self.item.init_expiry()
        await self.broadcast_embed()
        await self.bot.wait_until_ready()

    @on_bidding.after_loop
    async def post_bidding(self):
        # Status reset
        self.item = None


class CustomBidMoral(discord.ui.Modal, title="Custom Bid Form"):
    auction: Auction
    amount = discord.ui.TextInput(
        label="Amount", placeholder=f"Enter your bid ({MINIMUM_CALL_PRICE} up)"
    )

    def set_auction(self, auction: Auction) -> None:
        self.auction = auction

    async def on_submit(self, interaction: discord.Interaction) -> None:
        try:
            await self.auction.bid_action(interaction, int(self.amount.value))
        except ValueError:
            await interaction.response.send_message(
                "Invalid bid amount", ephemeral=True
            )