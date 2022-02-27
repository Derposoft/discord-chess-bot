from db.database import Game
import chess

# Takes two dictionaries and 2 lookups. Assigns the value if it exists otherwise assigns it to default
def safeDictCopyDefault(recv, recvpath, send, sendpath, default):
    safeDictCopy(recv, recvpath, send, sendpath, lambda: default)

# Takes two dictionaries and 2 lookups. Assigns the value if it exists otherwise calls supplier. Will not assign index to "None"
def safeDictCopy(recv, recvpath, send, sendpath, supplier=lambda: None):
    if recvpath is None or len(recvpath) == 0:
        raise ValueError("Indexes for receiving dictionary are empty or None") 
    elif sendpath is None or len(sendpath) == 0:
        raise ValueError("Indexes for sending dictionary are empty or None") 

    recvDict = recv
    recvNode = recv
    sendDict = send
    sendNode = send
    
    #TODO Maybe we should be type checking each node to be a dictionary or at least be
    #   indexable

    # Find Node in recv
    for i in range(len(recvpath)):
        index = recvpath[i]
        
        if index in recvNode:
            recvDict = recvNode
            recvNode = recvDict[index]
        elif i < len(recvpath) - 1:
            recvDict = recvNode
            recvDict[index] = {}
            recvNode = recvDict[index]
        else:
            recvDict = recvNode
    
    # Find Node in Send
    for index in sendpath:
        if index in sendNode:
            sendDict = sendNode
            sendNode = sendDict[index]
        else:
            sendNode = None
            break
    
    if sendNode is None:
        sendNode = supplier()
        if sendNode is None:
            return

    recvDict[recvpath[-1]] = sendNode

def _separate(moves):
    return [move for move in moves.split(' ') if move != '']

def parse_args(request):
    return request.args

def check_in_game(player_uid, db):
    return db.query(Game).filter_by(uid=player_uid).first()
def check_in_pvp(p1_uid, p2_uid, db):
    #print(f'checking {p1_uid},{p2_uid} and {p2_uid},{p1_uid}')
    p12 = f'{p1_uid},{p2_uid}'
    p21 = f'{p2_uid},{p1_uid}'
    p1p2 = db.query(Game).filter_by(uid=p12).first()
    p2p1 = db.query(Game).filter_by(uid=p21).first()
    print("GAMES FOUND", p1p2, p2p1)
    return  p1p2 if p1p2 else p2p1
        

def mention(args): # legacy method -- use mention_player and delet this
    return mention_player(args['uid'])
def mention_player(player_uid):
    return f'<@!{player_uid}>'

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
