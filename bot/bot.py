import discord
from discord.ext import commands
import json, requests, utils, sys, argparse, logging
import dummylog

### Get Command Line Arguments and configuration
description = """Discord Chess Bot is a simple application to play againt other server
members or to play against the Stockfish AI. Use -h or --help for information about the bot."""

argparser = argparse.ArgumentParser(description=description)
argparser.add_argument("-f", "--file", "--config", dest="configPath", default="./config.json", help = "File Path to Config File")
argparser.add_argument("-u", "--host", dest="url", default="http://localhost:5000/", help="url for acessing discord bot rest api")
argparser.add_argument("-l", "--log", dest="log", default="discord.log", help="output file path for debug logging!")
argparser.add_argument("--quiet", "--no-log", dest="quiet", default=False, action="store_const", const=True, help="Disable logging from bot. Not recommended!")
args = argparser.parse_args()

config = {
    'url': args.url,
    'log': args.log,
    'quiet': args.quiet
    }

print(f"Loading config file from {args.configPath}")
with open(args.configPath, 'r') as configFile:
    data = json.load(configFile)
    utils.safeDictCopy(config, ['key'], data, ['keys', 'discord'], lambda: print("No Key Provided to Bot!", file=sys.stderr))
    utils.safeDictCopy(config, ['url'], data, ['bot', 'url'])
    utils.safeDictCopy(config, ['password'], data, ['bot', 'password'])
    utils.safeDictCopyDefault(config, ['prefix'], data, ['bot', 'prefix'], '-')
    utils.safeDictCopyDefault(config, ['botDesc'], data, ['bot', 'description'], 'blindfold chess bot')
    utils.safeDictCopy(config, ['log'], data, ['bot', 'log'])

if 'key' not in config:
    exit(1)

### Initialize Log
if not config['quiet']:
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
else:
    logger = dummylog()

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

    logger.debug(f'Game Created By {ctx.author.id} with side {side} and elo {eloOrMention}')

    if utils.is_elo(eloOrMention):
        logger.debug(f'Creating Solo Game!')
        info = requests.get(config['url'] + 'new?side=' + side.lstrip().rstrip() 
            + '&elo=' + eloOrMention + '&' + utils.user_info(ctx))
    else:
        logger.debug(f'Creating 2 Player Game!')
        info = requests.get(config['url'] + 'new?side=' + side.lstrip().rstrip() 
            + '&challengee=' + utils.mention_parser(eloOrMention) + '&challenger=' + str(ctx.author.id))
    await ctx.send(info.text)

@bot.command()
async def move(ctx, move: str, player: str = ''):
    """makes a move in a currently running game. add an @mention at end for a pvp game."""

    logger.debug(f'Move made by {ctx.author.id} with move {move} against player \'{player}\'')
    info = requests.get(f'{config["url"]}move?move={move}&{utils.user_info(ctx)}{utils.pvpstring(player)}')
    await ctx.send(info.text)

@bot.command()
async def ff(ctx, player: str = ''):
    """resign the currently running game"""

    logger.debug(f'Forfeit yielded by {ctx.author.id} against player \'{player}\'')
    info = requests.get(f'{config["url"]}ff?{utils.user_info(ctx)}{utils.pvpstring(player)}')
    await ctx.send(info.text)

@bot.command()
async def cheat(ctx, player: str = ''):
    """allow the user to cheat by providing a boardstate and an evaluation. add an @mention at the end for a pvp game"""

    logger.debug(f'Cheat used by {ctx.author.id} against player \'{player}\'')
    info = requests.get(f'{config["url"]}cheat?{utils.user_info(ctx)}{utils.pvpstring(player)}')
    await ctx.send(info.text)

### Run the Bot Event Loop (infinite loop)
logger.debug("Running Bot!")
bot.run(config['key'])