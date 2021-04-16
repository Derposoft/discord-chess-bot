from db.database import Game
from stockfish import Stockfish
stockfish = Stockfish('/usr/games/stockfish')

def parse_args(request):
    return request.args

def check_in_game(player_uid, db):
    return db.query(Game).filter_by(uid=player_uid).first()

def mention(args):
    return ' <@' + args['uid'] + '> '

def check_move(moves, move):
    stockfish.set_position([move for move in moves if move != ''])
    return stockfish.is_move_correct(move)

def engine_move(moves, elo):
    print('currently-made moves', moves)
    stockfish.set_elo_rating(elo)
    stockfish.set_position([move for move in moves if move != ''])
    best = stockfish.get_best_move()
    return best

def relay_move(move, args):
    return ('I play ' + move + mention(args) + '.' if move != None else '')

def claim_victory(moves, args):
    stockfish.set_position([move for move in moves if move != ''])
    return mention(args) + 'get rekt noob i win again KEKW final board state:\n' + '```' + stockfish.get_board_visual() + '```'

def cheat_board(moves):
    stockfish.set_position([move for move in moves if move != ''])
    board = stockfish.get_board_visual()
    eval = stockfish.get_evaluation()
    best = stockfish.get_best_move()
    return '```' + board + '```', eval, best