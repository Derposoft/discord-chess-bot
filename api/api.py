from flask import Flask, url_for, request, make_response
from stockfish import Stockfish
import argparse, json

# Local Imports
import chessboard
import dao
import utils
import validation
from constants import BLACK, WHITE, STOCKFISH_INVITEE_ID


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
    utils.safe_dict_copy_default(config, ['stockfish-path'], data, ['api', 'stockfish', 'path'], '/usr/games/stockfish')
    utils.safe_dict_copy_default(config, ['stockfish-depth'], data, ['api', 'stockfish', 'depth'], 15)
    utils.safe_dict_copy_default(config, ['stockfish-params'], data, ['api', 'stockfish'], {})

dao.init(config['db'])
stockfish_app = Stockfish(path=config['stockfish-path'], depth=config['stockfish-depth'], parameters=config['stockfish-params'])

app = Flask(__name__)

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

@app.route('/change-user', methods = ['POST'])
def update_user():
    args = utils.parse_args(request)
    user_id = utils.get_first_valid_index(args, ['user'])
    guild_id = utils.get_first_valid_index(args, ['guild'])

    if dao.get_participant(user_id) == None:
        return make_response(f'That user doesn\'t exist pleb >:O', 401)
    
    if dao.update_participant(user_id, guild_id):
        return make_response(f'Update Done!', 201)
    
    return make_response(f'OH NO... WHY COULDN\'T I MAKE AN UPDATE ._.', 500)

@app.route('/get-user', methods = ['GET'])
def get_user():
    args = utils.parse_args(request)
    user_id = utils.get_first_valid_index(args, ['user'])

    user = dao.get_participant(user_id)
    if user == None:
        return make_response(f'That user doesn\'t exist pleb >:O', 401)
    
    return make_response(f'{user.id}', 200)

# creates a new game for the player
@app.route('/new-game/ai', methods = ['POST'])
def new_stockfish():
    args = utils.parse_args(request)
    author = utils.get_first_valid_index(args, ['author'])
    elo = utils.get_first_valid_index(args, ['elo'])
    side = utils.get_first_valid_index(args, ['side'])

    validation_resp = validation.validate_new_game(False, side, author, None)
    if validation_resp is not None:
        return validation_resp
    elif elo is None:
        return make_response(f'No Elo Setting Provided for AI Game!', 400)
    
     # check to make sure player doesn't already have a game
    participant = dao.get_participant(author)
    if participant is None:
        return make_response(f'Participant Does Not Exist!', 422)

    curr_game = dao.get_solo_game(participant)
    if curr_game != None:
        return make_response(f'bruh ur in a gam rn i will only ple 1 game with u at a time {utils.mention_player(author)}', 401)
    
    move = None
    player_is_white = side == WHITE
    dao.create_solo_game(participant, elo, player_is_white)
    if not player_is_white:
        move = chessboard.engine_move(stockfish_app, '', args['elo'])
        dao.add_move_to_game(curr_game, move, True)

    return make_response(f'New game successfully started for {utils.mention_player(author)}. {utils.relay_move(author, move)}', 200)


@app.route('/new-game/pvp', methods = ['POST'])    
def new():
    args = utils.parse_args(request)
    author = utils.get_first_valid_index(args, ['author'])
    invitee = utils.get_first_valid_index(args, ['invitee'])
    side = utils.get_first_valid_index(args, ['side'])

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
    curr_game = dao.get_pvp_game(author, invitee)
    if curr_game != None:
        return make_response(f'bruhh you can only ple 1 game with a given person at once {utils.mention_player(author)}', 401)
    
    author_is_white = side == WHITE
    dao.create_pvp_game(author_p, invitee_p, author_is_white)
    return f'New game successfully started between {utils.mention_player(author)} and {utils.mention_player(invitee)}.'

# make a move for the player
@app.route('/move',methods = ['POST', 'GET'])
def move():
    args = utils.parse_args(request)
    mover = utils.get_first_valid_index(args, ['self'])
    opponent = utils.get_first_valid_index(args, ['opponent'])
    is_ai = utils.get_first_valid_index(args, ['ai'])
    move_intent = utils.get_first_valid_index(args, ['move'])
    
    mover_p = dao.get_participant(mover)
    if mover_p is None:
        return make_response(f'bruh is this your first time {utils.mention_player(mover)}?', 400)
    
    opponent_p = None
    if opponent is not None:
        opponent_p = dao.get_participant(opponent)
        if opponent_p is None:
            return make_response(f'Cool you wanna play with {utils.mention_player(opponent)}... but idk who they are.', 400)
    
    is_pvp, game = get_game(mover_p, opponent_p, is_ai)

    if is_pvp:
        return move_pvp_game(mover_p, game, move_intent)
    else:
        return move_ai_game(mover_p, game, move_intent)

# accept the player's resignation
@app.route('/ff',methods = ['POST', 'GET'])
def ff():
    args = utils.parse_args(request)
    mover = utils.get_first_valid_index(args, ['self'])
    opponent = utils.get_first_valid_index(args, ['opponent'])
    is_pvp = opponent is not None

    mover_p = dao.get_participant(mover)
    if mover_p is None:
        return make_response(f'Maaaaaan, I donut even know u bruv {utils.mention_player(mover)}?', 400)

    game = None
    if is_pvp:
        opponent_p = dao.get_participant(opponent)
        if opponent_p is None:
            return make_response(f'You have a game \'gainst them? sure?', 400)

        game = dao.get_pvp_game(mover_p, opponent_p)
    else:
        game = dao.get_solo_game(mover_p)

    if game == None:
        return 'bruh don\'t know what game you speak of' + utils.mention_player(mover)

    moves = dao.get_moves_string(game)

    # resign the player and claim victory
    complete_game(game)

    if is_pvp:
        return pvp_claim_victory(moves, mover_p, opponent_p)
    else:
        return ai_claim_victory(moves, mover_p)

# allow the player to cheat
@app.route('/cheat',methods = ['POST', 'GET'])
def cheat():
    args = utils.parse_args(request)
    mover = utils.get_first_valid_index(args, ['self'])
    opponent = utils.get_first_valid_index(args, ['opponent'])
    is_ai = utils.get_first_valid_index(args, ['ai'])

    mover_p = dao.get_participant(mover)
    opponent_p = dao.get_participant(opponent)
    game = get_game(mover_p, opponent_p, is_ai)

    if game == None:
        return make_response(f'bruh don\'t know what game you speak of {utils.mention_player(mover)}', 400)

    # return cheats
    board, eval, best = chessboard.cheat_board(stockfish_app, game)

    return make_response(f'{board}\n{eval}\n{best}\nthat good enough for you? stupid cheater {utils.mention_player(mover)}', 200)


# TODO Make a file (seperate from utils) which accesses the database and is usable by the api
def move_ai_game(author, game, move_intent):
    moves = dao.get_moves_string(game)

    if not chessboard.check_move(stockfish_app, moves, move_intent):
        return make_response(f'u can\'t play that lol {utils.mention_db_player(author)}', 400)

    if not dao.add_move_to_game(game, move_intent, game.author_is_white):
        return make_response(f'Couldn\'t make that move in the DB Senpai!', 500)
        
    moves += move_intent

    # did player win?
    gameover_text = chessboard.get_gameover_text(app.logger, stockfish_app, moves, True)
    app.logger.debug(f"PLAYER MOVE GAMEOVER?: {gameover_text}")
    if gameover_text is not None:
        app.logger.debug("PLAYER WIN!")
        complete_game(game)
        return gameover_text

    # AI Player Takes Turn
    best_move = chessboard.engine_move(stockfish_app, game)
    dao.add_move_to_game(game, best_move, not game.author_is_white)
    moves = dao.get_moves_string(game)

    # Did AI Player Win?
    gameover_text = chessboard.get_gameover_text(app.logger, stockfish_app, moves, False)
    app.logger.debug(f"CPU MOVE GAMEOVER?: {gameover_text}")
    if gameover_text is not None:
        app.logger.debug("CPU WIN!")
        complete_game(game)
        return utils.relay_move_db(author, best_move) + '\n' + gameover_text

    return utils.relay_move_db(author, best_move)

def move_pvp_game(mover, game, move_intent):
    if not dao.check_users_turn(game, mover):
        return f'it not ur turn lol?? {utils.mention_db_player(mover)}'
    
    moves = dao.get_moves_string(game)

    # load the game in stockfish and verify that the move is legal
    if not chessboard.check_move(stockfish_app, moves, move_intent):
        return f'u can\'t play that lol {utils.mention_db_player(mover)}'

    if not dao.add_move_to_game(game, move_intent, utils.is_white_move(game.author_id, game.is_author_white, mover.id)):
        return make_response(f'Something Went Wrong in Making that Move (Are u hecking bro?)', 500)

    moves += move_intent

    # did player win?
    gameover_text = chessboard.get_gameover_text(app.logger, stockfish_app, moves, True)
    app.logger.debug(f"PLAYER MOVE GAMEOVER?: {gameover_text}")

    if gameover_text is not None:
        # end game
        app.logger.debug("PLAYER WIN!")
        complete_game(game)
        return gameover_text
        
    # did engine/person win?
    return f'ur move has been made good job pogO {utils.mention_db_player(mover)}'

def get_game(mover, opponent, is_ai):
    is_pvp = False
    game = None
    if opponent is None and not is_ai:
        game = dao.get_recent_game(mover)
        is_pvp = game.invitee_id == STOCKFISH_INVITEE_ID
    elif opponent is None:
        is_pvp = False
        game = dao.get_solo_game(mover)
    else:
        is_pvp = True
        game = dao.get_pvp_game(mover, opponent)
    
    return is_pvp, game

def complete_game(game):
    app.logger.debug(f'Game Has Been Completed and Thus Archived! ID:{game.id}')
    if not dao.archive_game(game):
        app.logger.error(f'Issue occurred when Archiving Game!')

def solo_claim_victory(moves, mover):
    return make_response(
        f'{utils.mention_db_player(mover)} is better than a rock with electricity...' +
        f'kudos to you with final board state:\n{chessboard.get_board_backquoted(stockfish_app, moves)}' +
        f'\nmoves: {moves}',
        201
    )

def ai_claim_victory(moves, mover):
    return make_response(
        f'{utils.mention_db_player(mover)} get rekt noob i win again KEKW ' +
        f'final board state:\n{chessboard.get_board_backquoted(stockfish_app, moves)}' +
        f'\nmoves: {moves}',
        201
    )

def pvp_claim_victory(moves, winner, loser):
    return make_response(
        f'{utils.mention_db_player(loser)} lmao ' +
        f'{utils.mention_db_player(winner)} stands above you again, you plebe:\n' + 
        f'{chessboard.get_board_backquoted(stockfish_app, moves)}' + 
        f'\nmoves: {moves}',
        201
    )

if __name__ == '__main__':
   app.run(debug = True)
