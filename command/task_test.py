import discord
from discord.ext import tasks, commands
from discord import TextChannel, app_commands
import discord.state
import discord.types
import asyncio

from config import MINIMUM_CALL_PRICE, MY_GUILD_ID_OBJECT

# 定義名為 TaskTest 的 Cog
class TaskTest(commands.Cog):
    bot: commands.Bot
    interact_channel: TextChannel | None
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.counter = 0
        self.interact_channel = None

    # 前綴指令
    @commands.command()
    async def TaskTest(self, ctx: commands.Context):
        print(ctx.message)
        await ctx.send("pong!")

    @app_commands.command(name = "tasktest", description = "Test task looping")
    @app_commands.guilds(MY_GUILD_ID_OBJECT)
    async def tasktest(self, interaction: discord.Interaction):
        self.interact_channel = interaction.channel
        # 回覆使用者的訊息
        await interaction.response.send_message("Preparing task")
        await self.run_task.start()

    @app_commands.command(name = "embeddedtest", description = "Test embedded")
    @app_commands.guilds(MY_GUILD_ID_OBJECT)
    async def embeddedtest(self, interaction: discord.Interaction):
        player_id = 14817468
        embed = discord.Embed(title="Bidding (stllok)", url=f"https://osu.ppy.sh/users/{player_id}", description="In-Queue: 42\tUnsold: 2\tSold: 1")
        embed.add_field(name="Expiry in", value="<t:1725970740:R>")
        embed.add_field(name="Price", value=10)
        embed.add_field(name="Qualify Seed", value="WIP")
        embed.add_field(name="ETX Rating", value=6.99)
        embed.add_field(name="Skill Issue Rating", value=7000)
        embed.add_field(name="Current Caller", value=None)
        embed.set_image(url=f"https://a.ppy.sh/{player_id}")
        embed.set_footer(text="Use below button for **Bid Increment**")
        
        view = discord.ui.View()
        
        button = discord.ui.Button(label="TEST")
        
        button.callback = lambda i: i.response.send_message("hello")
        
        view.add_item(item=button)
        view.add_item(item=discord.ui.Button(label=f"Minimum (+{MINIMUM_CALL_PRICE})"))
        view.add_item(item=discord.ui.Button(label="+50"))
        view.add_item(item=discord.ui.Button(label="+100"))
        view.add_item(item=discord.ui.Button(label="+250"))
        view.add_item(item=discord.ui.Button(label="+500"))
        
        await interaction.response.send_message(view=view, embed=embed)

    @tasks.loop(seconds=1, count=5)
    async def run_task(self):
        self.counter += 1
        await self.interact_channel.send(f"{self.counter} second(s) passed")
        
        
    @run_task.before_loop
    async def before_task(self):
        self.counter = 0
        await self.interact_channel.send("Starting task...")
        
        await asyncio.sleep(5)
        await self.bot.wait_until_ready()
        
    @run_task.after_loop
    async def after_task(self):
        await self.interact_channel.send("task finished!")
        