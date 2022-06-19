import discord
from discord.ext import commands
import json, requests, sys, argparse, logging
from . import utils

### Get Command Line Arguments and configuration
description = """Discord Chess Bot is a simple application to play againt other server
members or to play against the Stockfish AI. Use -h or --help for information about the bot."""

argparser = argparse.ArgumentParser(description=description)
argparser.add_argument(
    "--file",
    "--config",
    dest="configPath",
    default="./config.json",
    help="File Path to Config File",
)
argparser.add_argument(
    "--host",
    dest="url",
    default="http://localhost:5000/",
    help="url for acessing discord bot rest api",
)
argparser.add_argument(
    "--log",
    dest="log",
    default="discord.log",
    help="output file path for debug logging!",
)
argparser.add_argument(
    "--quiet",
    "--no-log",
    dest="quiet",
    default=False,
    action="store_const",
    const=True,
    help="Disable logging from bot. Not recommended!",
)
args = argparser.parse_args()

config = {"url": args.url, "log": args.log, "quiet": args.quiet}

print(f"Loading config file from {args.configPath}")
with open(args.configPath, "r") as configFile:
    data = json.load(configFile)
    utils.safe_dict_copy(config, ["key"], data, ["keys", "discord"])
    utils.safe_dict_copy(config, ["url"], data, ["bot", "url"])
    utils.safe_dict_copy(config, ["password"], data, ["bot", "password"])
    utils.safe_dict_copy(config, ["prefix"], data, ["bot", "prefix"], "-")
    utils.safe_dict_copy(
        config, ["botDesc"], data, ["bot", "description"], "blindfold chess bot"
    )
    utils.safe_dict_copy(config, ["log"], data, ["bot", "log"])

if "key" not in config:
    print("No Key Provided to Bot!", file=sys.stderr)
    exit(1)

### Initialize Log
logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)

# According to Pydocs we shouldn't be Instantiating handlers...
# but regardless this option is available to users. 
# If it becomes less useful we can remove it later
if config["quiet"]:
    handler = logging.NullHandler()
    logger.addHandler(handler)
else:
    handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
    handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    )
    logger.addHandler(handler)
    


### Initialize bot
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(
    command_prefix=config["prefix"], description=config["botDesc"], intents=intents
)

userID = None

### Bot Events and Commands
@bot.event
async def on_ready():
    global userID
    userID = bot.user.id
    logger.debug(f"logged on as {bot.user.name}{userID}!")


@bot.command()
async def signup(ctx):
    """Mostly for Debugging. Signs up a user to the platform (memorizes the user and guild ids)"""

    logger.debug(f"Signing up User!")
    info = requests.post(f'{config["url"]}signup?' + f"user={ctx.author.id}")
    await ctx.send(info.text)


@bot.command()
async def new(ctx, side: str, eloOrMention: str = "1500"):
    """starts a new chess game VS CPU/human for the current user given an option of side: b, w, or r (random)."""

    logger.debug(
        f"Game Created By {ctx.author.id} with side {side} and elo {eloOrMention}"
    )

    if userID != None and eloOrMention == userID:
        logger.debug(f"User tried to start a game with the bot... how naieve!")
        await ctx.send("Thanks, but I am too busy to play right now!")
        return

    if utils.is_elo(eloOrMention):
        logger.debug(f"Creating Solo Game!")
        info = requests.post(
            f'{config["url"]}new-game/ai?'
            + f"side={side.lstrip().rstrip()}"
            + f"&elo={eloOrMention}"
            + f"&author={utils.user_info(ctx)}"
        )
    else:
        logger.debug(f"Creating 2 Player Game!")
        info = requests.post(
            f'{config["url"]}new-game/pvp?'
            + f"side={side.lstrip().rstrip()}"
            + f"&invitee={utils.mention_parser(eloOrMention)}"
            + f"&author={utils.user_info(ctx)}"
        )
    await ctx.send(info.text)


@bot.command()
async def move(ctx, move: str, player: str = ""):
    """makes a move in a currently running game. add an @mention at end for a pvp game."""

    logger.debug(
        f"Move made by {ctx.author.id} with move {move} against player '{player}'"
    )

    ai_query_arg = ""
    opponent_query_arg = ""
    if player != "" and player != "!":
        opponent_query_arg = f"&opponent={utils.pvpstring(player)}"
    elif player == "!":
        ai_query_arg = "&ai=true"

    info = requests.post(
        f'{config["url"]}move?'
        + f"move={move}"
        + f"&self={utils.user_info(ctx)}"
        + opponent_query_arg
        + ai_query_arg
    )

    await ctx.send(info.text)


@bot.command()
async def ff(ctx, player: str = ""):
    """resign the currently running game"""

    logger.debug(f"Forfeit yielded by {ctx.author.id} against player '{player}'")

    ai_query_arg = ""
    opponent_query_arg = ""
    if player != "" and player != "!":
        opponent_query_arg = f"&opponent={utils.pvpstring(player)}"
    elif player == "!":
        ai_query_arg = "&ai=true"

    info = requests.post(
        f'{config["url"]}ff?'
        + f"self={utils.user_info(ctx)}"
        + opponent_query_arg
        + ai_query_arg
    )
    await ctx.send(info.text)


@bot.command()
async def cheat(ctx, player: str = ""):
    """allow the user to cheat by providing a boardstate and an evaluation. add an @mention at the end for a pvp game"""

    logger.debug(f"Cheat used by {ctx.author.id} against player '{player}'")

    ai_query_arg = ""
    opponent_query_arg = ""
    if player != "" and player != "!":
        opponent_query_arg = f"&opponent={utils.pvpstring(player)}"
    elif player == "!":
        ai_query_arg = "&ai=true"

    info = requests.get(
        f'{config["url"]}cheat?'
        + f"self={utils.user_info(ctx)}"
        + opponent_query_arg
        + ai_query_arg
    )
    await ctx.send(info.text)


### Run the Bot Event Loop (infinite loop)
print("Running Bot!")
bot.run(config["key"])
