import discord
from discord.ext import commands
import json
import requests
from datetime import datetime
import utils
import config
import os

# initialize bot
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='-', description='blindfold chess bot', intents=intents)
@bot.event
async def on_ready():
    print('logged on as {0}{1}!'.format(bot.user.name, bot.user.id))

@bot.command()
async def new(ctx, side: str, elo: str = '1500'):
    """starts a new chess game VS CPU/human for the current user given an option of side: b, w, or r (random)."""
    if utils.is_elo(elo):
        info = requests.get(config.API_URI + 'new?side=' + side.lstrip().rstrip() 
            + '&elo=' + elo + '&' + utils.user_info(ctx))
    else:
        info = requests.get(config.API_URI + 'new?side=' + side.lstrip().rstrip() 
            + '&challengee=' + utils.mention_parser(elo) + '&challenger=' + str(ctx.author.id))
    await ctx.send(info.text)

@bot.command()
async def move(ctx, move: str, player: str = ''):
    """makes a move in a currently running game. add an @mention at end for a pvp game."""
    info = requests.get(f'{config.API_URI}move?move={move}&{utils.user_info(ctx)}{utils.pvpstring(player)}')
    await ctx.send(info.text)

@bot.command()
async def ff(ctx, player: str = ''):
    """resign the currently running game"""
    info = requests.get(f'{config.API_URI}ff?{utils.user_info(ctx)}{utils.pvpstring(player)}')
    await ctx.send(info.text)

@bot.command()
async def cheat(ctx, player: str = ''):
    """allow the user to cheat by providing a boardstate and an evaluation. add an @mention at the end for a pvp game"""
    info = requests.get(f'{config.API_URI}cheat?{utils.user_info(ctx)}{utils.pvpstring(player)}')
    await ctx.send(info.text)

keys = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys.json'), 'r'))
bot.run(keys.get('discord'))