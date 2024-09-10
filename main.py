# 導入Discord.py模組
import discord
from discord.ext import commands

# 導入commands指令模組

import os

from ossapi import Ossapi

from command.ping import Ping
from command.task_test import TaskTest
from config import CAPTAIN_ROLE_ID, CHANNEL_ID, DISCORD_TOKEN, MY_GUILD_ID, MY_GUILD_ID_OBJECT, OSUAPI_ID, OSUAPI_SECRET, OWNER_USERID, PLAYER_ROLE_ID
from bot_struct.captain import Captain


# intents是要求機器人的權限
intents = discord.Intents.all()
# command_prefix是前綴符號，可以自由選擇($, #, &...)
bot = commands.Bot(command_prefix = "%", intents = intents)
osuapi = Ossapi(OSUAPI_ID, OSUAPI_SECRET)

COGS = [Ping(bot), TaskTest(bot)]


# 當機器人完成啟動
@bot.event
async def on_ready():
    captains = list(map(Captain, filter(lambda member: member.get_role(CAPTAIN_ROLE_ID) is not None, (bot.get_channel(CHANNEL_ID)).members)))
    players = list(map(Captain, filter(lambda member: member.get_role(PLAYER_ROLE_ID) is not None, (bot.get_channel(CHANNEL_ID)).members)))
    print(f"Initialize captain and member complete!")
    
    for cog in COGS:
        await bot.add_cog(cog)
    print(f"載入 {len(await bot.tree.sync(guild=MY_GUILD_ID_OBJECT))} 個斜線指令")
    print(f"目前登入身份 --> {bot.user}")
    
@bot.command()
async def sync(ctx):
    print("sync command")
    if ctx.author.id == OWNER_USERID:
        slash = await bot.tree.sync()
        await ctx.send('Command tree synced.')
        print(f"載入 {len(slash)} 個斜線指令")
    else:
        await ctx.send('You must be the owner to use this command!')
    

bot.run(DISCORD_TOKEN)