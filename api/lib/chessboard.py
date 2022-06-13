import chess, logging

logger = logging.getLogger(__name__)

def _set_board_to(stockfish, moves):
    stockfish.set_position(
        [move for move in moves.split(' ') if move != '']
    )

def check_move(stockfish, moves, move):
    _set_board_to(stockfish, moves)
    return stockfish.is_move_correct(move)

def engine_move(stockfish, moves, elo):
    stockfish.set_elo_rating(elo)
    _set_board_to(stockfish, moves)
    best = stockfish.get_best_move()
    return best

def cheat_board(stockfish, moves):
    logger.debug(f'moves {moves}')
    _set_board_to(stockfish, moves)
    board = stockfish.get_board_visual()
    eval = stockfish.get_evaluation()
    best = stockfish.get_best_move()
    return '```' + board + '```', str(eval), best

def get_board(stockfish, moves):
    _set_board_to(stockfish, moves)
    return stockfish.get_board_visual()

def get_board_backquoted(stockfish, moves):
    return f'```{get_board(stockfish, moves)}```'

def get_gameover_text(stockfish, moves, player_just_moved):
    logger.debug(f'{moves} {player_just_moved}')
    board_visual = get_board_backquoted(stockfish, moves)
    finish_text = board_visual + '\nfull game: ' + moves
    fen = stockfish.get_fen_position()
    board = chess.Board(fen)
    logger.debug(f'{board.outcome()}')
    # check for different game over scenarios
    if board.is_stalemate():
        return 'game is draw by stalemate. sadge. final board:\n' + finish_text
    elif board.is_insufficient_material():
        return 'game is draw by not enough juicers for mate sadge. final board:\n' + finish_text
    elif board.can_claim_fifty_moves():
        return 'game is draw by 50 move rule OMEGALUL:\n' + finish_text
    elif board.can_claim_threefold_repetition():
        return 'game is over by 3fold repetition :LUL: :\n' + finish_text
    elif board.is_checkmate():
        if player_just_moved:
            return 'you win POG game over, well played ((no kap)). final board:\n' + finish_text
        else:
            return 'i win POG game over, well played ((hard kap)). final board:\n' + finish_text
    elif board.outcome() != None:
        return 'game is over by unknown glitch (jk it\'s a chess rule but i haven\'t coded it in :\n' + finish_text

    return None
