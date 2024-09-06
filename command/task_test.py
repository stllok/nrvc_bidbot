import discord
from discord.ext import tasks, commands
from discord import TextChannel, app_commands

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

    @tasks.loop(seconds=1, count=5)
    async def run_task(self):
        self.counter += 1
        await self.interact_channel.send(f"{self.counter} second(s) passed")
        
        
    @run_task.before_loop
    async def before_task(self):
        self.counter = 0
        await self.interact_channel.send("Starting task...")
        await self.bot.wait_until_ready()
        
    @run_task.after_loop
    async def after_task(self):
        await self.interact_channel.send("task finished!")
        