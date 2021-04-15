import discord
from discord.ext import commands
from commands import stocks
import json
import requests
import config
from datetime import datetime

# initialize bot
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='-', description='portfolio-tracking bot', intents=intents)
@bot.event
async def on_ready():
    print('logged on as {0}{1}!'.format(bot.user.name, bot.user.id))

@bot.command()
async def quote(ctx, ticker: str):
    """ticker: quote stock's price from ticker"""
    info = requests.get(config.API_URI + 'quotes/' + ticker.lstrip().rstrip()).text
    await ctx.send(info)

@bot.command()
async def list(ctx):
    """: list your portfolio"""
    print(ctx.author.id)
    info = requests.get(config.API_URI + 'trades?uid=' + str(ctx.author.id))
    await ctx.send(info.text)

@bot.command()
async def buy(ctx, ticker: str, num_shares: int, init_price: int, date: str=str(datetime.now().isoformat())):
    """ticker x y date: log a purchase of x shares of a ticker's stock at $y on the given date. price and date optional"""
    confirmation = await stocks.buy(ctx, ticker, num_shares, init_price, date)
    await ctx.send(
        '{0} bought {1} shares of {2}.'.format(ctx.author.name, num_shares, ticker)
        if confirmation else 
        'There was a problem placing that order. Please check your shit, idiot.'
    )

@bot.command()
async def sell(ctx, ticker: str, num_shares: int, init_price: int, date: str=str(datetime.now().isoformat())):
    """ticker x y date: log a selloff of x shares of a ticker's stock at $y on the given date. price and date optional"""
    confirmation = await stocks.sell(ctx, ticker, num_shares, init_price, date)
    await ctx.send(
        '{0} sold {1} shares of {2}.'.format(ctx.author.name, num_shares, ticker)
        if confirmation else 
        'There was a problem placing that order. Please check your shit, idiot.'
    )

keys = json.load(open('keys.json', 'r'))
bot.run(keys.get('discord'))