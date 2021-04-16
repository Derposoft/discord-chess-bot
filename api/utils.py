from db.database import Game
from stockfish import Stockfish
stockfish = Stockfish('/usr/games/stockfish')

def _separate(moves):
    return [move for move in moves.split(' ') if move != '']

def parse_args(request):
    return request.args

def check_in_game(player_uid, db):
    return db.query(Game).filter_by(uid=player_uid).first()

def mention(args):
    return ' <@' + args['uid'] + '> '

def check_move(moves, move):
    stockfish.set_position(_separate(moves))
    return stockfish.is_move_correct(move)

def engine_move(moves, elo):
    stockfish.set_elo_rating(elo)
    stockfish.set_position(_separate(moves))
    best = stockfish.get_best_move()
    return best

def relay_move(move, args):
    return ('I play ' + move + mention(args) + '.' if move != None else '')

def claim_victory(moves, args):
    stockfish.set_position(_separate(moves))
    return mention(args) + 'get rekt noob i win again KEKW final board state:\n' + '```' + stockfish.get_board_visual() + '```'

def cheat_board(moves):
    stockfish.set_position(_separate(moves))
    board = stockfish.get_board_visual()
    eval = stockfish.get_evaluation()
    best = stockfish.get_best_move()
    return '```' + board + '```', str(eval), best