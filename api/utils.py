from db.database import Game
from stockfish import Stockfish
import chess
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
    return mention(args) + 'get rekt noob i win again KEKW final board state:\n' + '```' + stockfish.get_board_visual() + '```' + '\nmoves: ' + moves

def cheat_board(moves):
    stockfish.set_position(_separate(moves))
    board = stockfish.get_board_visual()
    eval = stockfish.get_evaluation()
    best = stockfish.get_best_move()
    return '```' + board + '```', str(eval), best

def get_gameover_text(moves, player_just_moved):
    stockfish.set_position(_separate(moves))
    board_visual = '```' + stockfish.get_board_visual() + '```'
    finish_text = board_visual + '\nfull game: ' + moves
    fen = stockfish.get_fen_position()
    board = chess.Board(fen)
    # check for different game over scenarios
    if board.is_stalemate():
        return 'game is draw by stalemate. sadge. final board:\n' + finish_text
    elif board.is_insufficient_material():
        return 'game is draw by not enough juicers for mate sadge. final board:\n' + finish_text
    elif board.can_claim_fifty_moves():
        return 'game is draw by 50 move rule OMEGALUL:\n' + finish_text
    elif board.can_claim_threefold_repetition():
        return 'game is over by 3fold repetition :thinking: :\n' + finish_text
    elif board.outcome() != None:
        if board.outcome().winner:
            if player_just_moved:
                return 'you win POG game over, well played ((no kap)). final board:\n' + finish_text
            else:
                return 'i win POG game over, well played ((hard kap)). final board:\n' + finish_text
    return ''
