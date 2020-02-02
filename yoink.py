# yoink: moves your lampstand to discord
# currently only a hello world

import discord
from discord.ext import commands
from secrets import discord_bot_token

bot = commands.Bot(command_prefix='Lampstand: ')

@bot.command()
async def ping(ctx):
    await ctx.send('pong')

print ("Launching bot")
bot.run(discord_bot_token)

