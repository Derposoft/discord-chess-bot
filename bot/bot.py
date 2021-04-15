import discord
from discord.ext import commands
import json
import requests
from datetime import datetime
import utils
import config

# initialize bot
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='-', description='blindfold chess bot', intents=intents)
@bot.event
async def on_ready():
    print('logged on as {0}{1}!'.format(bot.user.name, bot.user.id))

@bot.command()
async def new(ctx, side: str):
    """starts a new chess game for the current user given an option of side: b, w, or r (random)"""
    info = requests.get(config.API_URI + 'new?side=' + side.lstrip().rstrip()).text + '&' + utils.send_user(ctx)
    await ctx.send(info)

@bot.command()
async def move(ctx, move):
    """makes a move in the currently running game"""
    print(ctx.author.id)
    info = requests.get(config.API_URI + 'move?move=' + move + '&' + utils.send_user(ctx))
    await ctx.send(info.text)

@bot.command()
async def ff(ctx):
    """resign the currently running game"""
    info = requests.get(config.API_URI + 'ff?' + + utils.send_user(ctx))
    await ctx.send(info)

@bot.command()
async def cheat(ctx, ticker: str, num_shares: int, init_price: int, date: str=str(datetime.now().isoformat())):
    """allow the user to cheat by providing a boardstate and an evaluation"""
    info = requests.get(config.API_URI + 'cheat?' + + utils.send_user(ctx))
    await ctx.send()

keys = json.load(open('bot/keys.json', 'r'))
bot.run(keys.get('discord'))