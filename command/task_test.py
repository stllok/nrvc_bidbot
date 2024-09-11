import discord
from discord.ext import tasks, commands
from discord import TextChannel, app_commands
import discord.state
import discord.types
import asyncio

from config import MY_GUILD_ID_OBJECT

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
        await interaction.response.send_message(f"Preparing task")
        await self.run_task.start()

    @app_commands.command(name = "embeddedtest", description = "Test embedded")
    @app_commands.guilds(MY_GUILD_ID_OBJECT)
    async def embeddedtest(self, interaction: discord.Interaction):
        id = 14817468
        embed = discord.Embed(title="Bidding (stllok)", url=f"https://osu.ppy.sh/users/{id}", description="In-Queue: 42\tUnsold: 2\tSold: 1")
        embed.add_field(name="Expiry in", value="<t:1725970740:R>")
        embed.add_field(name="Price", value=10)
        embed.add_field(name="Qualify Seed", value="WIP")
        embed.add_field(name="ETX Rating", value=6.99)
        embed.add_field(name="Skill Issue Rating", value=7000)
        embed.add_field(name="Current Caller", value=None)
        embed.set_image(url=f"https://a.ppy.sh/{id}")
        embed.set_footer(text="Use below button for **Bid Increment**")
        
        view = discord.ui.View()
        
        button = discord.ui.Button(label="Bid")
        
        button.callback = lambda i: i.response.send_message("hello")
        
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
        