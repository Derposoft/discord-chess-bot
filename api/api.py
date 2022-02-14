from utils import check_in_game, mention, mention_player, parse_args, engine_move,\
    check_move, check_in_pvp, relay_move, claim_victory, cheat_board, get_gameover_text
from flask import Flask, url_for, request
from db.database import db_session, Game

app = Flask(__name__)

# creates a new game for the player
@app.route('/new')
def new():
    args = parse_args(request)
    db = db_session()
    # check to make sure player only chose black or white
    if args['side'] != 'white':
        if args['side'] != 'black':
            return 'you can only be \'white\' or \'black\' because this is chess OMEGALUL'
    # this is a pvp game
    game_id = ''
    is_pvp = 'challenger' in args
    if is_pvp:
        curr_game = check_in_pvp(args['challenger'], args['challengee'], db)
        if curr_game != None:
            return f'bruhh you can only ple 1 game with a given person at once {mention(args)}'
        game_id = f'{args["challenger"]},{args["challengee"]}'
    # this is a vs CPU game
    else:
        # check to make sure player doesn't already have a game
        curr_game = check_in_game(args['uid'], db)
        if curr_game != None:
            return f'bruh ur in a gam rn i will only ple 1 game with u at a time {mention(args)}'
        game_id = args['uid']
    # check to see which side player is
    move = None
    if args['side'] == 'black' and is_pvp:
        # make a move and game to db if player is black and vs CPU
        move = engine_move('', args['elo'])
    # i'm using the stockfish_elo to hold which player's turn it is because i'm lazy. ez hack no judge me pls
    elo = args['elo'] if not is_pvp else args['side'] == 'black'
    game = Game(uid=game_id, moves=move, stockfish_elo=elo, player_side=args['side'])
    db.add(game)
    db.commit()
    # report back
    info_string = ''
    if is_pvp:
        p1, p2 = args['challenger'], args['challengee']
        info_string = f'New game successfully started between {mention_player(p1)} and {mention_player(p2)}.'
    else:
        info_string = f'New game successfully started for {mention(args)}. {relay_move(move, args)}'
    return info_string

# make a move for the player
@app.route('/move',methods = ['POST', 'GET'])
def move():
    args = parse_args(request)
    # check to make sure player is in a game
    db = db_session()
    curr_game = check_in_game(args['uid'], db)
    if curr_game == None:
        return f'bruh ur not in a game rn {mention(args)}'
    # load the game in stockfish and verify that the move is legal
    if not check_move(curr_game.moves, args['move']):
        return f'u can\'t play that lol {mention(args)}'
    # if move is legal, add the move
    new_moves = curr_game.moves + ' ' + args['move']
    # did player win?
    gameover_text = get_gameover_text(new_moves, player_just_moved=True)
    print("PLAYER MOVE GAMEOVER?: ", gameover_text)
    if gameover_text != '':
        # end game
        print("PLAYER WIN!")
        db.delete(curr_game)
        return gameover_text
    # make engine move    
    best = engine_move(new_moves, curr_game.stockfish_elo)
    new_moves = new_moves + ' ' + best
    curr_game.moves = new_moves
    # did engine win?
    gameover_text = get_gameover_text(new_moves, player_just_moved=False)
    print("CPU MOVE GAMEOVER?: ", gameover_text)
    if gameover_text != '':
        # end game
        print("CPU WIN!")
        db.delete(curr_game)
        return relay_move(best, args) + '\n' + gameover_text
    db.commit()
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
