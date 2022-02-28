import chess

def _separate(moves):
    return [move for move in moves.split(' ') if move != '']

def check_move(stockfish, moves, move):
    stockfish.set_position(_separate(moves))
    return stockfish.is_move_correct(move)

def engine_move(stockfish, moves, elo):
    stockfish.set_elo_rating(elo)
    stockfish.set_position(_separate(moves))
    best = stockfish.get_best_move()
    return best

def relay_move(move, args):
    return ('I play ' + move + mention(args) + '.' if move != None else '')

def claim_victory(stockfish, moves, args):
    stockfish.set_position(_separate(moves))
    return mention(args) + 'get rekt noob i win again KEKW final board state:\n' + '```' + stockfish.get_board_visual() + '```' + '\nmoves: ' + moves

def pvp_claim_victory(stockfish, moves, args):
    stockfish.set_position(_separate(moves))
    return f'{mention(args)} lmao {mention_player(args["opponent"])} stands above you again, you plebe:\n' + '```' + stockfish.get_board_visual() + '```' + '\nmoves: ' + moves

def cheat_board(stockfish, moves):
    print('moves', moves)
    stockfish.set_position(_separate(moves))
    board = stockfish.get_board_visual()
    eval = stockfish.get_evaluation()
    best = stockfish.get_best_move()
    return '```' + board + '```', str(eval), best

def get_gameover_text(stockfish, moves, player_just_moved):
    print(moves, player_just_moved)
    stockfish.set_position(_separate(moves))
    board_visual = '```' + stockfish.get_board_visual() + '```'
    finish_text = board_visual + '\nfull game: ' + moves
    fen = stockfish.get_fen_position()
    board = chess.Board(fen)
    print(board.outcome())
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
    return ''
