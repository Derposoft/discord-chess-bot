from logging import root
from flask import Flask, request, Blueprint
from stockfish import Stockfish
import argparse, json, sys, logging

# Local Imports
from . import chessboard, query, utils, validation, game_utils
from .constants import BLACK, WHITE, STOCKFISH_INVITEE_ID

# BUG (see chessboard.py)
stockfish_app = None

# Other modules may load logger by using
#  logger = logging.getLogger('some name here')
logger = None

root = Blueprint('root', __name__)

@root.route('/signup', methods = ['POST'])
def create_user():
    args = utils.parse_args(request)
    user_id = utils.get_first_valid_index(args, ['user'])
    guild_id = utils.get_first_valid_index(args, ['guild'])
    if user_id == None and guild_id == None:
        return utils.respond(f'Cannot Sign This User Up without some Discord Identification', 400)
    
    if query.get_participant(user_id) != None:
        return utils.respond(f'That user already exists Master -.o', 401)
    
    if query.get_participant(guild_id) != None:
        return utils.respond(f'That user already exists Master -.o', 401)

    if query.create_participant(user_id, guild_id):
        return utils.respond(f'Created User M8!', 201)
    
    return utils.respond(f'UWU I couldn\'t make that for you senpai >.<', 500)

@root.route('/change-user', methods = ['POST'])
def update_user():
    args = utils.parse_args(request)
    user_id = utils.get_first_valid_index(args, ['user'])
    guild_id = utils.get_first_valid_index(args, ['guild'])
    
    if query.get_participant(user_id) == None:
        return utils.respond(f'That user doesn\'t exist pleb >:O', 401)
    
    if query.update_participant(user_id, guild_id):
        return utils.respond(f'Update Done!', 202)
    
    return utils.respond(f'OH NO... WHY COULDN\'T I MAKE AN UPDATE ._.', 500)

@root.route('/get-user', methods = ['GET'])
def get_user():
    args = utils.parse_args(request)
    user_id = utils.get_first_valid_index(args, ['user'])

    user = query.get_participant(user_id)
    if user == None:
        return utils.respond(f'That user doesn\'t exist pleb >:O', 401)
    
    return utils.respond(f'{user.discord_guild_id}', 200)

# creates a new game for the player
@root.route('/new-game/ai', methods = ['POST'])
def new_stockfish():
    args = utils.parse_args(request)
    author = utils.get_first_valid_index(args, ['author'])
    elo = utils.get_first_valid_index(args, ['elo'])
    side = utils.get_first_valid_index(args, ['side'])

    validation_resp = validation.validate_new_game(False, side, author, None)
    if validation_resp is not None:
        return validation_resp
    elif elo is None:
        return utils.respond(f'No Elo Setting Provided for AI Game!', 400)
    
     # check to make sure player doesn't already have a game
    participant = query.get_participant(author)
    if participant is None:
        return utils.respond(f'Participant Does Not Exist!', 422)

    curr_game = query.get_solo_game(participant)
    if curr_game != None:
        return utils.respond(f'bruh ur in a gam rn i will only ple 1 game with u at a time {utils.mention_player(author)}', 401)
    
    move = None
    player_is_white = side == WHITE
    query.create_solo_game(participant, elo, player_is_white)
    if not player_is_white:
        move = chessboard.engine_move(stockfish_app, '', args['elo'])
        query.add_move_to_game(curr_game, move, True)

    return utils.respond(f'New game successfully started for {utils.mention_player(author)}. {utils.relay_move(author, move)}', 201)


@root.route('/new-game/pvp', methods = ['POST'])    
def new():
    args = utils.parse_args(request)
    author = utils.get_first_valid_index(args, ['author'])
    invitee = utils.get_first_valid_index(args, ['invitee'])
    side = utils.get_first_valid_index(args, ['side'])

    validation_resp = validation.validate_new_game(True, side, author, invitee)
    if validation_resp is not None:
        return utils.respond(validation_resp, 400)
    
    # check to make sure player doesn't already have a game
    author_p = query.get_participant(author)
    if author_p is None:
        return utils.respond(f'Author Participant Does Not Exist!', 430)
    
    invitee_p = query.get_participant(invitee)
    if invitee_p is None:
        return utils.respond(f'Author Participant Does Not Exist!', 430)

    logger.debug(f'Attempting Creation for pvp game {author} and {invitee}')
    curr_game = query.get_pvp_game(author, invitee)
    if curr_game != None:
        return utils.respond(f'bruhh you can only ple 1 game with a given person at once {utils.mention_player(author)}', 401)
    
    author_is_white = side == WHITE
    query.create_pvp_game(author_p, invitee_p, author_is_white)
    return utils.respond(f'New game successfully started between {utils.mention_player(author)} and {utils.mention_player(invitee)}.', 201)

# make a move for the player
@root.route('/move',methods = ['POST', 'GET'])
def move():
    args = utils.parse_args(request)
    mover = utils.get_first_valid_index(args, ['self'])
    opponent = utils.get_first_valid_index(args, ['opponent'])
    is_ai = utils.get_first_valid_index(args, ['ai'])
    move_intent = utils.get_first_valid_index(args, ['move'])
    
    logger.debug(f"THIS IS A COOL MOVE INTENT {move_intent}")
    if move_intent is None:
        return utils.respond(f'WTH you want me to come up with the move for you {utils.mention_player(mover)}?!!!')

    response = game_utils.get_game(mover, opponent, is_ai)
    if not response.is_valid():
        return response.get_error()
    
    mover_p = response.get_mover()
    is_pvp = response.get_is_pvp()
    game = response.get_game()

    if is_pvp:
        return game_utils.move_pvp_game(mover_p, game, move_intent, stockfish_app)
    else:
        return game_utils.move_ai_game(mover_p, game, move_intent, stockfish_app)

# accept the player's resignation
@root.route('/ff',methods = ['POST', 'GET'])
def ff():
    args = utils.parse_args(request)
    mover = utils.get_first_valid_index(args, ['self'])
    opponent = utils.get_first_valid_index(args, ['opponent'])
    is_ai = utils.get_first_valid_index(args, ['ai'])
    
    response = game_utils.get_game(mover, opponent, is_ai)
    if not response.is_valid():
        return response.get_error()
    
    mover_p = response.get_mover()
    opponent_p = response.get_opponent()
    is_pvp = response.get_is_pvp()
    game = response.get_game()

    moves = query.get_moves_string(game)

    # resign the player and claim victory
    game_utils.complete_game(game)

    if is_pvp:
        return game_utils.pvp_claim_victory(moves, mover_p, opponent_p, stockfish_app)
    else:
        return game_utils.ai_claim_victory(moves, mover_p, stockfish_app)

# allow the player to cheat
@root.route('/cheat',methods = ['POST', 'GET'])
def cheat():
    args = utils.parse_args(request)
    mover = utils.get_first_valid_index(args, ['self'])
    opponent = utils.get_first_valid_index(args, ['opponent'])
    is_ai = utils.get_first_valid_index(args, ['ai'])

    response = game_utils.get_game(mover, opponent, is_ai)
    if not response.is_valid():
        return response.get_error()
    
    game = response.get_game()

    # return cheats
    board, eval, best = chessboard.cheat_board(stockfish_app, game)

    return utils.respond(f'{board}\n{eval}\n{best}\nthat good enough for you? stupid cheater {utils.mention_player(mover)}', 200)

# Startup code
CONFIG_PATH_DEST = "configPath"

def command_line_parse(argv = sys.argv):
    description = """Chess Move Restful API"""

    argparser = argparse.ArgumentParser(description=description)
    argparser.add_argument("--file", "--config", dest=CONFIG_PATH_DEST, default="./config.json", help = "File Path to Config File")
    argparser.add_argument("--db", "--database", dest="db", help="SQL URI for accessing SQL database")
    return vars(argparser.parse_args(argv))

def create_app(args={}):
    config = {}

    # There is also config file loading that comes with json from flask's library
    #   especially if you don't like this hacky code
    data = {}
    if CONFIG_PATH_DEST in args:
        print(f"Loading config file from {args[CONFIG_PATH_DEST]}")
        with open(args[CONFIG_PATH_DEST], 'r') as configFile:
            data = json.load(configFile)

    # From Config File
    utils.safe_dict_copy_default(config, ['host'], data, ['api', 'host'], "0.0.0.0")
    utils.safe_dict_copy_default(config, ['port'], data, ['api', 'port'], 8000)
    utils.safe_dict_copy_default(config, ['stockfish-path'], data, ['api', 'stockfish', 'path'], '/usr/games/stockfish')
    utils.safe_dict_copy_default(config, ['stockfish-depth'], data, ['api', 'stockfish', 'depth'], 15)
    utils.safe_dict_copy_default(config, ['stockfish-params'], data, ['api', 'stockfish'], {})
    utils.safe_dict_copy_default(config, ['flask'], data, ['api', 'flask'], {})
    utils.safe_dict_copy(config, ['db'], data, ['api', 'db_uri'])

    # From CLI Args
    utils.safe_dict_copy_default(config, ['db'], args, ['db'], "sqlite:///storage.db")

    query.init(config['db'])
    global stockfish_app
    stockfish_app = Stockfish(path=config['stockfish-path'], depth=config['stockfish-depth'], parameters=config['stockfish-params'])

    app = Flask(__name__)
    app.config.update(config['flask'])
    app.register_blueprint(root)

    global logger
    logger = app.logger
    logger.setLevel(logging.DEBUG)
    return app

def main():
    args = command_line_parse()
    app = create_app(args)
    app.run(debug = True)

## TODO Needed a different project structure for unit testing. Is this still needed?
if __name__ == "__main__":
    main()