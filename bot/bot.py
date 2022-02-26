import discord
from discord.ext import commands
import json, requests, utils, sys, os, argparse

### Get Command Line Arguments and configuration
description = """Discord Chess Bot is a simple application to play againt other server
members or to play against the Stockfish AI. Use -h or --help for information about the bot."""

argparser = argparse.ArgumentParser(description=description)
argparser.add_argument("-f", "--file", "--config", dest="configPath", default="./config.json", help = "File Path to Config File")
argparser.add_argument("-u", "--host", dest="url", default="http://localhost:5000", help="url for acessing discord bot rest api")
args = argparser.parse_args()

config = {'url': args.url}

print(f"Loading config file from {args.configPath}")
with open(args.configPath, 'r') as configFile:
    data = json.load(configFile)
    utils.safeDictCopy(config, ['key'], data, ['keys', 'discord'], lambda: print("No Key Provided to Bot!", file=sys.stderr))
    utils.safeDictCopy(config, ['url'], data, ['api', 'url'])
    utils.safeDictCopy(config, ['password'], data, ['api', 'password'])
    utils.safeDictCopyDefault(config, ['prefix'], data, ['bot', 'prefix'], '-')
    utils.safeDictCopyDefault(config, ['botDesc'], data, ['bot', 'description'], 'blindfold chess bot')

### Initialize bot
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=config['prefix'], description=config['botDesc'], intents=intents)


### Bot Events and Commands

@bot.event
async def on_ready():
    print(f'logged on as {bot.user.name}{bot.user.id}!')

@bot.command()
async def new(ctx, side: str, eloOrMention: str = '1500'):
    """starts a new chess game VS CPU/human for the current user given an option of side: b, w, or r (random)."""

    if utils.is_elo(eloOrMention):
        info = requests.get(config['url'] + 'new?side=' + side.lstrip().rstrip() 
            + '&elo=' + eloOrMention + '&' + utils.user_info(ctx))
    else:
        info = requests.get(config['url'] + 'new?side=' + side.lstrip().rstrip() 
            + '&challengee=' + utils.mention_parser(eloOrMention) + '&challenger=' + str(ctx.author.id))
    await ctx.send(info.text)

@bot.command()
async def move(ctx, move: str, player: str = ''):
    """makes a move in a currently running game. add an @mention at end for a pvp game."""

    info = requests.get(f'{config["url"]}move?move={move}&{utils.user_info(ctx)}{utils.pvpstring(player)}')
    await ctx.send(info.text)

@bot.command()
async def ff(ctx, player: str = ''):
    """resign the currently running game"""

    info = requests.get(f'{config["url"]}ff?{utils.user_info(ctx)}{utils.pvpstring(player)}')
    await ctx.send(info.text)

@bot.command()
async def cheat(ctx, player: str = ''):
    """allow the user to cheat by providing a boardstate and an evaluation. add an @mention at the end for a pvp game"""

    info = requests.get(f'{config["url"]}cheat?{utils.user_info(ctx)}{utils.pvpstring(player)}')
    await ctx.send(info.text)

### Run the Bot Event Loop (infinite loop)
bot.run(config['key'])