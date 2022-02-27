from flask import Flask, url_for, request
from db.database import init, db_session, Game
from stockfish import Stockfish
import argparse, json, logging
import dummylog, utils

### Get Command Line Arguments and configuration
description = """Chess Move Restful API"""

argparser = argparse.ArgumentParser(description=description)
argparser.add_argument("-f", "--file", "--config", dest="configPath", default="./config.json", help = "File Path to Config File")
argparser.add_argument("--db", "--database", dest="db", default="sqlite:///storage.db", help="SQL URI for accessing SQL database")
argparser.add_argument("-l", "--log", dest="log", default="api.log", help="output file path for debug logging!")
argparser.add_argument("--quiet", "--no-log", dest="quiet", default=False, action="store_const", const=True, help="Disable logging from bot. Not recommended!")
args = argparser.parse_args()

config = {
    'db': args.db,
    'log': args.log,
    'quiet': args.quiet
    }

print(f"Loading config file from {args.configPath}")
with open(args.configPath, 'r') as configFile:
    data = json.load(configFile)
    utils.safe_dict_copy_default(config, ['host'], data, ['api', 'host'], "0.0.0.0")
    utils.safe_dict_copy_default(config, ['port'], data, ['api', 'port'], 8000)
    utils.safe_dict_copy_default(config, ['stockfish'], data, ['api', 'stockfish'], '/usr/games/stockfish')
    utils.safe_dict_copy(config, ['log'], data, ['bot', 'log'])

### Initialize Log
if not config['quiet']:
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
else:
    logger = dummylog()

init(config['db'])
stockfish = Stockfish(config['stockfish'])

app = Flask(__name__)

# creates a new game for the player
@app.route('/new')
def new():
    args = utils.parse_args(request)
    db = db_session()
    side = args['side']
    # TODO challengee is very close to challenger... maybe the parameter should
    #    be something more distinguished? P1 versus P2? Author vs Invitee?
    author = utils.get_first_valid_index(args, ['challengee', 'uid'])
    invitee = utils.get_first_valid_index(args, ['challenger'])
    elo = utils.get_first_valid_index(args, ['elo'])

    # check to make sure player only chose black or white
    if side != 'white' and side != 'black':
        return 'you can only be \'white\' or \'black\' because this is chess OMEGALUL'
    elif author is None:
        return 'A unique ID for the player must be provided!'

    # this is a pvp game
    game_id = ''
    is_pvp = 'challenger' in args
    if is_pvp:
        logger.debug(author, invitee)
        curr_game = utils.check_in_pvp(author, invitee, db)
        if curr_game != None:
            return f'bruhh you can only ple 1 game with a given person at once {utils.mention_player(author)}'
        game_id = f'{author},{invitee}'

    # this is a vs CPU game
    else:
        # check to make sure player doesn't already have a game
        curr_game = utils.check_in_game(author, db)
        if curr_game != None:
            return f'bruh ur in a gam rn i will only ple 1 game with u at a time {utils.mention(args)}'
        game_id = args['uid']
    logger.debug(f'choosing game id {game_id}')

    # check to see which side player is
    move = ''
    if side == 'black' and not is_pvp:
        # make a move and game to db if player is black and vs CPU
        move = utils.engine_move(stockfish, '', args['elo'])

    # i'm using the stockfish_elo to hold which player's turn it is because i'm lazy. ez hack no judge me pls
    elo = elo if not is_pvp else args['side'] == 'black'
    game = Game(uid=game_id, moves=move, stockfish_elo=elo, player_side=args['side'])
    db.add(game)
    db.commit()

    # report back
    info_string = ''
    if is_pvp:
        p1, p2 = args['challenger'], args['challengee']
        info_string = f'New game successfully started between {utils.mention_player(p1)} and {utils.mention_player(p2)}.'
    else:
        info_string = f'New game successfully started for {utils.mention(args)}. {utils.relay_move(move, args)}'
    return info_string

# make a move for the player
@app.route('/move',methods = ['POST', 'GET'])
def move():
    args = utils.parse_args(request)
    is_pvp = 'opponent' in args
    db = db_session()
    # check to make sure player is in a game
    curr_game = None
    if is_pvp:
        curr_game = utils.check_in_pvp(args['uid'], args['opponent'], db)
    else:
        curr_game = utils.check_in_game(args['uid'], db)
    if curr_game == None:
        pvp_addon = f' with {utils.mention_player(args["opponent"])}' if is_pvp else ''
        return f'bruh ur not in a game rn {utils.mention(args)}{pvp_addon}'
    # if pvp, ensure that it is the player's turn
    if is_pvp:
        player_num = curr_game.stockfish_elo
        if args['uid'] != curr_game.uid.split(',')[player_num]:
            return f'it not ur turn lol?? {utils.mention(args)}'
    # load the game in stockfish and verify that the move is legal
    if not utils.check_move(stockfish, curr_game.moves, args['move']):
        return f'u can\'t play that lol {utils.mention(args)}'
    # if move is legal, add the move (and switch player turn if pvp)
    new_moves = curr_game.moves + ' ' + args['move']
    if is_pvp:
        curr_game.stockfish_elo = 1-curr_game.stockfish_elo
    # did player win?
    gameover_text = utils.get_gameover_text(stockfish, new_moves, player_just_moved=True)
    logger.debug(f"PLAYER MOVE GAMEOVER?: {gameover_text}")
    if gameover_text != '':
        # end game
        logger.debug("PLAYER WIN!")
        db.delete(curr_game)
        return gameover_text
    # make engine move if vs cpu
    if not is_pvp:
        best = utils.engine_move(stockfish, new_moves, curr_game.stockfish_elo)
        new_moves = new_moves + ' ' + best
    curr_game.moves = new_moves
    # did engine/person win?
    gameover_text = utils.get_gameover_text(stockfish, new_moves, player_just_moved=False)
    logger.debug(f"CPU MOVE GAMEOVER?: {gameover_text}")
    if gameover_text != '':
        # end game
        logger.debug("CPU WIN!")
        db.delete(curr_game)
        return utils.relay_move(best, args) + '\n' + gameover_text
    db.commit()
    if is_pvp:
        return 'ur move has been made good job pogO'
    return utils.relay_move(best, args)

# accept the player's resignation
@app.route('/ff',methods = ['POST', 'GET'])
def ff():
    args = utils.parse_args(request)
    is_pvp = 'opponent' in args
    db = db_session()
    # check to make sure player is in a game
    curr_game = None
    if is_pvp:
        curr_game = utils.check_in_pvp(args['uid'], args['opponent'], db)
    else:
        curr_game = utils.check_in_game(args['uid'], db)
    if curr_game == None:
        return 'bruh ur not in a game rn' + utils.mention(args)
    # resign the player and claim victory
    db.delete(curr_game)
    db.commit()
    if not is_pvp:
        return utils.claim_victory(stockfish, curr_game.moves, args)
    else:
        return utils.pvp_claim_victory(stockfish, curr_game.moves, args)

# allow the player to cheat
@app.route('/cheat',methods = ['POST', 'GET'])
def cheat():
    args = utils.parse_args(request)
    is_pvp = 'opponent' in args
    db = db_session()
    # check to make sure player is in a game
    curr_game = None
    if is_pvp:
        curr_game = utils.check_in_pvp(args['uid'], args['opponent'], db)
    else:
        curr_game = utils.check_in_game(args['uid'], db)
    if curr_game == None:
        return 'bruh ur not in a game rn' + utils.mention(args)
    # return cheats
    board, eval, best = utils.cheat_board(stockfish, curr_game.moves)

    return board + '\n' + eval + '\n' + best + '\n' + 'that good enough for you? stupid cheater' + utils.mention(args)

if __name__ == '__main__':
   app.run(debug = True)
