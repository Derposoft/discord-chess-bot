from flask import Flask, url_for, request
from db.database import init, db_session, GameLegacy,\
    Participant, StockfishGame, StockfishMoves, CompetitiveGame, CompetitiveMoves
from stockfish import Stockfish
import argparse, json
import utils

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

init(config['db'])
stockfish = Stockfish(config['stockfish'])

app = Flask(__name__)

WHITE = 'white'
BLACK = 'black'

# TODO We should provide HTTP Status codes for this API if we want to support it long-term

# creates a new game for the player
@app.route('/new/ai', methods = ['POST'])
def new_stockfish():
    args = utils.parse_args(request)
    db = db_session()
    side = args['side']
    author = utils.get_first_valid_index(args, ['author'])
    elo = utils.get_first_valid_index(args, ['elo'])

    validation = validate_new_game(False, side, author, None)
    if validation is not None:
        return validation
    elif elo is None:
        return f'No Elo Setting Provided for AI Game!'
    
     # check to make sure player doesn't already have a game
    curr_game = utils.check_in_game(author, db)
    if curr_game != None:
        return f'bruh ur in a gam rn i will only ple 1 game with u at a time {utils.mention(args)}'
    
    player_is_white = side == WHITE
    if not player_is_white:
        # make a move and game to db if player is black and vs CPU
        move = utils.engine_move(stockfish, '', args['elo'])
    
    # TODO author id FK failure
    game = StockfishGame(partipant_id=author, stockfish_elo=elo, player_is_white=player_is_white)
    db.add(game)
    db.commit()

    return f'New game successfully started for {utils.mention(author)}. {utils.relay_move(move, args)}'


@app.route('/new/pvp', methods = ['POST'])    
def new():
    args = utils.parse_args(request)
    db = db_session()
    side = args['side']
    author = utils.get_first_valid_index(args, ['author'])
    invitee = utils.get_first_valid_index(args, ['invitee'])

    validation = validate_new_game(True, side, author, invitee)
    if validation is not None:
        return validation

    app.logger.debug(f'Attempting Creation for pvp game {author} and {invitee}')
    curr_game = utils.check_in_pvp(author, invitee, db)
    if curr_game != None:
        return f'bruhh you can only ple 1 game with a given person at once {utils.mention_player(author)}'
    
    author_is_white=side == WHITE
    game = CompetitiveGame(author_id=author, invitee_id=invitee, author_is_white=author_is_white)
    db.add(game)
    db.commit()

    return f'New game successfully started between {utils.mention_player(author)} and {utils.mention_player(invitee)}.'

def validate_new_game(is_pvp, side, author, invitee):
    if side != 'white' and side != 'black':
        return 'you can only be \'white\' or \'black\' because this is chess OMEGALUL'
    elif author is None:
        return 'A unique ID for the author must be provided!'
    elif is_pvp and invitee is None:
        return 'A unique ID for the invitee/challenged must be provided!'
    
    return None

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
    db = db_session()
    # check to make sure player is in a game
    game = utils.check_in_game(mover, db)

    if game is None:
        # pvp_addon = f' with {utils.mention_player(args["opponent"])}' if is_pvp else ''
        return f'bruh ur not in a solo game rn {utils.mention(args)}'
    
    if not utils.check_move(stockfish, game, move_intent):
        return f'u can\'t play that lol {utils.mention(args)}'
    
    best = utils.engine_move(stockfish, game)

    # did player win?
    gameover_text = utils.get_gameover_text(stockfish, game)
    app.logger.debug(f"PLAYER MOVE GAMEOVER?: {gameover_text}")

    if gameover_text is not None:
        # end game
        app.logger.debug("PLAYER WIN!")
        utils.complete_game(game)
        return gameover_text

    gameover_text = utils.get_gameover_text(stockfish, game)
    app.logger.debug(f"CPU MOVE GAMEOVER?: {gameover_text}")
    if gameover_text != '':
        # end game
        app.logger.debug("CPU WIN!")
        utils.complete_game(game)
        return utils.relay_move(best, args) + '\n' + gameover_text
    db.commit()

    return utils.relay_move(best, args)


def move_pvp(args, mover, opponent, move_intent):
    db = db_session()
    game = utils.check_in_game(mover, db)

    if game is None:
        # pvp_addon = f'  ''
        result = f'bruh ur not in a solo game rn {utils.mention(args)}'
        + f'with {utils.mention_player(args["opponent"])}'
        
        return result

    if not utils.check_movers_turn(game, mover, db):
        return f'it not ur turn lol?? {utils.mention(args)}'
    
    # load the game in stockfish and verify that the move is legal
    if not utils.check_move(stockfish, game, move_intent):
        return f'u can\'t play that lol {utils.mention(args)}'

    # if move is legal, add the move (and switch player turn if pvp)
    if not utils.make_move(game, mover, move_intent):
        return f'Something Went Wrong in Making that Move (Are u hecking bro?)'
    
    # did player win?
    gameover_text = utils.get_gameover_text(stockfish, game)
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
    db = db_session()
    mover = utils.get_first_valid_index(args, ['self'])
    opponent = utils.get_first_valid_index(args, ['opponent'])

    is_pvp, game = get_game(db, args, mover, opponent)

    if game == None:
        return 'bruh don\'t know what game you speak of' + utils.mention(mover)

    # resign the player and claim victory
    utils.complete_game(game)

    if is_pvp:
        return utils.claim_victory(stockfish, game)
    else:
        return utils.claim_victory(stockfish, game)

# allow the player to cheat
@app.route('/cheat',methods = ['POST', 'GET'])
def cheat():
    args = utils.parse_args(request)
    db = db_session()
    mover = utils.get_first_valid_index(args, ['self'])
    opponent = utils.get_first_valid_index(args, ['opponent'])

    _, game = get_game(db, args, mover, opponent)

    if game == None:
        return 'bruh don\'t know what game you speak of' + utils.mention(mover)

    # return cheats
    board, eval, best = utils.cheat_board(stockfish, game)

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
