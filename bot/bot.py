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
    """starts a new chess game VS CPU for the current user given an option of side: b, w, or r (random)"""
    info = requests.get(config.API_URI + 'new?side=' + side.lstrip().rstrip() 
        + '&elo=' + elo + '&' + utils.user_info(ctx))
    await ctx.send(info.text)
@bot.command()
async def newpvp(ctx, side: str, player: str):
    """starts a new chess game VS @mention for the current user given an option of side: b, w, or r (random)"""
    challenger_uid = utils.user_info(ctx)
    challengee_uid = player[3:-1] # cuts out the '<@!' and '>' and the start and end
    info = requests.get(config.API_URI + 'new?side=' + side.lstrip().rstrip() 
        + '&challengee=' + challengee_uid + '&challenger=' + challenger_uid)
    await ctx.send(info.text)

@bot.command()
async def move(ctx, move: str, player: str = ''):
    """makes a move in a currently running game. add an @mention at end for a pvp game."""
    pstring = ''
    if player != '':
        # is a pvp game
        pstring = f'&opponent={player}'
    info = requests.get(f'{config.API_URI}move?move={move}&{utils.user_info(ctx)}{pstring}')
    await ctx.send(info.text)

@bot.command()
async def ff(ctx):
    """resign the currently running game"""
    info = requests.get(config.API_URI + 'ff?' + utils.user_info(ctx))
    await ctx.send(info.text)

@bot.command()
async def cheat(ctx):
    """allow the user to cheat by providing a boardstate and an evaluation"""
    info = requests.get(config.API_URI + 'cheat?' + utils.user_info(ctx))
    await ctx.send(info.text)

keys = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys.json'), 'r'))
bot.run(keys.get('discord'))