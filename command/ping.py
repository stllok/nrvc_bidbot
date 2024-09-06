import discord
from discord import app_commands
from discord.ext import commands

from bot import NRVCBot
from config import MY_GUILD_ID_OBJECT


# 定義名為 Ping 的 Cog
class Ping(commands.Cog):
    bot: commands.Bot

    def __init__(self, bot: NRVCBot):
        self.bot = bot

    # 前綴指令
    @commands.command()
    async def Ping(self, ctx: commands.Context):
        await ctx.send("Hello, world!")

    @app_commands.command(name="ping", description="Pong!")
    @app_commands.guilds(MY_GUILD_ID_OBJECT)
    async def ping(self, interaction: discord.Interaction):
        # 回覆使用者的訊息
        await interaction.response.send_message("pong!")
        await (await self.bot.create_dm(interaction.user)).send(
            "Hello it is a DM pong!"
        )
