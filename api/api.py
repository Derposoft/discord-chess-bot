from utils import check_in_game, mention, parse_args
from flask import Flask, url_for, request
from stockfish import Stockfish
stockfish = Stockfish('/usr/games/stockfish')
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
    # otherwise check to see which side player is
    if args['side'] == 'white':
        # add game to db if player is white
        game = Game(uid=args['uid'], moves='', stockfish_elo=args['elo'])
        db.add(game)
        db.commit()
    elif args['side'] == 'black':
        # make a move and game to db if player is black
        game = Game(uid=args['uid'], moves='', stockfish_elo=args['elo'])
        db.add(game)
        db.commit()

    # report back
    return 'New game successfully started for %s' % args['name']

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
    stockfish.set_position([move for move in curr_game.moves if move != ''])

    return 'under construction'


# accept the player's resignation
@app.route('/ff',methods = ['POST', 'GET'])
def ff():
    return 'under construction'


# allow the player to cheat
@app.route('/cheat',methods = ['POST', 'GET'])
def cheat():
    return 'under construction'

if __name__ == '__main__':
   app.run(debug = True)