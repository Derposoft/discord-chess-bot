from utils import check_in_game, mention, parse_args, engine_move, check_move, relay_move, claim_victory, cheat_board, get_gameover_text
from flask import Flask, url_for, request
from db.database import db_session, Game

app = Flask(__name__)

# creates a new game for the player
@app.route('/new')
def new():
    args = parse_args(request)
    # check to make sure player only chose black or white
    if args['side'] != 'white':
        if args['side'] != 'black':
            return 'you can only be \'white\' or \'black\' because this is chess OMEGALUL'
    # check to make sure player doesn't already have a game
    db = db_session()
    curr_game = check_in_game(args['uid'], db)
    if curr_game != None:
        return 'bruh ur in a gam rn i will only ple 1 game with u at a time' + mention(args)
    # check to see which side player is
    move = None
    if args['side'] == 'white':
        # add game to db if player is white
        game = Game(uid=args['uid'], moves='', stockfish_elo=args['elo'], player_side='white')
        db.add(game)
        db.commit()
    elif args['side'] == 'black':
        # make a move and game to db if player is black
        move = engine_move('', args['elo'])
        game = Game(uid=args['uid'], moves=move, stockfish_elo=args['elo'], player_side='black')
        db.add(game)
        db.commit()
    # report back
    return 'New game successfully started for %s' % args['name'] + '. ' + relay_move(move, args)

# make a move for the player
@app.route('/move',methods = ['POST', 'GET'])
def move():
    args = parse_args(request)
    # check to make sure player is in a game
    db = db_session()
    curr_game = check_in_game(args['uid'], db)
    if curr_game == None:
        return 'bruh ur not in a game rn' + mention(args)
    # load the game in stockfish and verify that the move is legal
    if not check_move(curr_game.moves, args['move']):
        return 'u can\'t play that lol' + mention(args)
    # if move is legal, add the move
    new_moves = curr_game.moves + ' ' + args['move']
    # did player win?
    gameover_text = get_gameover_text(new_moves, player_just_moved=True)
    print("PLAYER MOVE GAMEOVER?: ", gameover_text)
    if gameover_text != '':
        # end game
        db.delete(curr_game)
        return gameover_text
    # make engine move    
    best = engine_move(new_moves, curr_game.stockfish_elo)
    new_moves = new_moves + ' ' + best
    curr_game.moves = new_moves
    db.commit()
    # did engine win?
    gameover_text = get_gameover_text(new_moves, player_just_moved=False)
    print("CPU MOVE GAMEOVER?: ", gameover_text)
    if gameover_text != '':
        # end game
        db.delete(curr_game)
        return relay_move(best, args) + '\n' + gameover_text
    return relay_move(best, args)

# accept the player's resignation
@app.route('/ff',methods = ['POST', 'GET'])
def ff():
    args = parse_args(request)
    # check to make sure player is in a game
    db = db_session()
    curr_game = check_in_game(args['uid'], db)
    if curr_game == None:
        return 'bruh ur not in a game rn' + mention(args)
    # resign the player and claim victory
    db.delete(curr_game)
    db.commit()
    return claim_victory(curr_game.moves, args)

# allow the player to cheat
@app.route('/cheat',methods = ['POST', 'GET'])
def cheat():
    args = parse_args(request)
    # check to make sure player is in a game
    db = db_session()
    curr_game = check_in_game(args['uid'], db)
    if curr_game == None:
        return 'bruh ur not in a game rn' + mention(args)
    # return cheats
    board, eval, best = cheat_board(curr_game.moves)

    return board + '\n' + eval + '\n' + best + '\n' + 'that good enough for you? stupid cheater' + mention(args)

if __name__ == '__main__':
   app.run(debug = True)