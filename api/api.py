from flask import Flask, url_for, request, make_response
from stockfish import Stockfish
import argparse, json

# Local Imports
import chessboard
import dao
import utils
import validation


### Get Command Line Arguments and configuration
description = """Chess Move Restful API"""

argparser = argparse.ArgumentParser(description=description)
argparser.add_argument("-f", "--file", "--config", dest="configPath", default="./config.json", help = "File Path to Config File")
argparser.add_argument("--db", "--database", dest="db", default="sqlite:///storage.db", help="SQL URI for accessing SQL database")
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

dao.init(config['db'])
stockfish_app = Stockfish(config['stockfish'])

app = Flask(__name__)

WHITE = 'white'
BLACK = 'black'

@app.route('/signup', methods = ['POST'])
def create_user():
    args = utils.parse_args(request)
    user_id = utils.get_first_valid_index(args, ['user'])
    guild_id = utils.get_first_valid_index(args, ['guild'])
    if user_id == None and guild_id == None:
        return make_response(f'Cannot Sign This User Up without some Discord Identification', 400)
    
    if dao.get_participant(user_id) != None:
        return make_response(f'That user already exists Master -.o', 401)
    
    if dao.get_participant(guild_id) != None:
        return make_response(f'That user already exists Master -.o', 401)

    if dao.create_participant(user_id, guild_id):
        return make_response(f'Created User M8!', 202)
    
    return make_response(f'UWU I couldn\'t make that for you sir >.<', 500)

# TODO Create an UPDATE user Method

# creates a new game for the player
@app.route('/new/ai', methods = ['POST'])
def new_stockfish():
    args = utils.parse_args(request)
    side = args['side']
    author = utils.get_first_valid_index(args, ['author'])
    elo = utils.get_first_valid_index(args, ['elo'])

    validation_resp = validation.validate_new_game(False, side, author, None)
    if validation_resp is not None:
        return validation_resp
    elif elo is None:
        return make_response(f'No Elo Setting Provided for AI Game!', 400)
    
     # check to make sure player doesn't already have a game
    participant = dao.get_participant(author)
    if participant is None:
        return make_response(f'Participant Does Not Exist!', 422)

    curr_game = dao.check_in_solo(participant)
    if curr_game != None:
        return make_response(f'bruh ur in a gam rn i will only ple 1 game with u at a time {utils.mention(args)}', 401)
    
    player_is_white = side == WHITE
    dao.create_stockfish_game(participant, elo, player_is_white)
    if not player_is_white:
        #TODO
        # make a move and game to db if player is black and vs CPU
        move = chessboard.engine_move(stockfish_app, '', args['elo'])

    return make_response(f'New game successfully started for {utils.mention(author)}. {utils.relay_move(move, args)}', 200)


@app.route('/new/pvp', methods = ['POST'])    
def new():
    args = utils.parse_args(request)
    side = args['side']
    author = utils.get_first_valid_index(args, ['author'])
    invitee = utils.get_first_valid_index(args, ['invitee'])

    validation_resp = validation.validate_new_game(True, side, author, invitee)
    if validation_resp is not None:
        return make_response(validation_resp, 400)
    
    # check to make sure player doesn't already have a game
    author_p = dao.get_participant(author)
    if author_p is None:
        return make_response(f'Author Participant Does Not Exist!', 430)
    
    invitee_p = dao.get_participant(invitee)
    if invitee_p is None:
        return make_response(f'Author Participant Does Not Exist!', 430)

    app.logger.debug(f'Attempting Creation for pvp game {author} and {invitee}')
    curr_game = dao.check_in_pvp(author, invitee)
    if curr_game != None:
        return make_response(f'bruhh you can only ple 1 game with a given person at once {utils.mention_player(author)}', 401)
    
    author_is_white=side == WHITE
    dao.create_competitive_game(author_p, invitee_p, author_is_white)
    return f'New game successfully started between {utils.mention_player(author)} and {utils.mention_player(invitee)}.'

# make a move for the player
@app.route('/move',methods = ['POST', 'GET'])
def move():
    args = utils.parse_args(request)
    mover = utils.get_first_valid_index(args, ['self'])
    opponent = utils.get_first_valid_index(args, ['opponent'])
    move_intent = utils.get_first_valid_index(args, ['move'])
    
    if opponent is None:
        return move_most_recent(args, mover, move_intent)
    elif opponent == "!":
        return move_ai(args, mover, move_intent)
    else:
        return move_pvp(args, mover, opponent, move_intent)

def move_most_recent(args, mover, move_intent):
    pass

def move_ai(args, mover, move_intent):
    # check to make sure player is in a game
    game = dao.check_in_solo(mover)

    if game is None:
        # pvp_addon = f' with {utils.mention_player(args["opponent"])}' if is_pvp else ''
        return f'bruh ur not in a solo game rn {utils.mention(args)}'
    
    if not chessboard.check_move(stockfish_app, game, move_intent):
        return f'u can\'t play that lol {utils.mention(args)}'
    
    best = chessboard.engine_move(stockfish_app, game)

    # did player win?
    gameover_text = utils.get_gameover_text(stockfish_app, game)
    app.logger.debug(f"PLAYER MOVE GAMEOVER?: {gameover_text}")

    if gameover_text is not None:
        # end game
        app.logger.debug("PLAYER WIN!")
        utils.complete_game(game)
        return gameover_text

    gameover_text = chessboard.get_gameover_text(stockfish_app, game)
    app.logger.debug(f"CPU MOVE GAMEOVER?: {gameover_text}")
    if gameover_text != '':
        # end game
        app.logger.debug("CPU WIN!")
        utils.complete_game(game)
        return utils.relay_move(best, args) + '\n' + gameover_text

    return utils.relay_move(best, args)


def move_pvp(args, mover, opponent, move_intent):
    game = utils.check_in_pvp(mover, opponent)

    if game is None:
        # pvp_addon = f'  ''
        result = f'bruh ur not in a solo game rn {utils.mention(args)}'
        + f'with {utils.mention_player(args["opponent"])}'
        
        return result

    if not utils.check_movers_turn(game, mover):
        return f'it not ur turn lol?? {utils.mention(args)}'
    
    # load the game in stockfish and verify that the move is legal
    if not chessboard.check_move(stockfish_app, game, move_intent):
        return f'u can\'t play that lol {utils.mention(args)}'

    # if move is legal, add the move (and switch player turn if pvp)
    if not utils.make_move(game, mover, move_intent):
        return f'Something Went Wrong in Making that Move (Are u hecking bro?)'
    
    # did player win?
    gameover_text = chessboard.get_gameover_text(stockfish_app, game)
    app.logger.debug(f"PLAYER MOVE GAMEOVER?: {gameover_text}")

    if gameover_text is not None:
        # end game
        app.logger.debug("PLAYER WIN!")
        utils.complete_game(game)
        return gameover_text
        
    # did engine/person win?
    return f'ur move has been made good job pogO {utils.mention(args)}'
    

# accept the player's resignation
@app.route('/ff',methods = ['POST', 'GET'])
def ff():
    args = utils.parse_args(request)
    mover = utils.get_first_valid_index(args, ['self'])
    opponent = utils.get_first_valid_index(args, ['opponent'])

    is_pvp, game = get_game(db, args, mover, opponent)

    if game == None:
        return 'bruh don\'t know what game you speak of' + utils.mention(mover)

    # resign the player and claim victory
    utils.complete_game(game)

    if is_pvp:
        return chessboard.claim_victory(stockfish_app, game)
    else:
        return chessboard.claim_victory(stockfish_app, game)

# allow the player to cheat
@app.route('/cheat',methods = ['POST', 'GET'])
def cheat():
    args = utils.parse_args(request)
    mover = utils.get_first_valid_index(args, ['self'])
    opponent = utils.get_first_valid_index(args, ['opponent'])

    _, game = get_game(db, args, mover, opponent)

    if game == None:
        return 'bruh don\'t know what game you speak of' + utils.mention(mover)

    # return cheats
    board, eval, best = chessboard.cheat_board(stockfish_app, game)

    return board + '\n' + eval + '\n' + best + '\n' + 'that good enough for you? stupid cheater' + utils.mention(args)

def get_game(db, args, mover, opponent):
    is_pvp = False
    game = None
    if opponent is None:
        game, is_pvp = utils.get_most_recent_game(db, args, mover)
    elif opponent == "!":
        is_pvp = True
        game = utils.get_ai_game(db, args, mover)
    else:
        is_pvp = False
        game = utils.get_pvp_game(db, args, mover)
    
    return is_pvp, game

if __name__ == '__main__':
   app.run(debug = True)
