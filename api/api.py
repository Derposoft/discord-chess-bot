from flask import Flask, url_for, request
from stockfish import Stockfish
stockfish = Stockfish('/usr/games/stockfish')
from db.Game import Game
from db.database import db_session
import utils

app = Flask(__name__)

# creates a new game for the player
@app.route('/new')
def new():
    args = utils.parse_args(request)
    # check to make sure player doesn't already have a game
    session = db_session()
    curr_game = session.query(Game).filter_by(uid=args['uid']).first()
    if curr_game != None:
        return 'bruh ur in a gam rn i will only ple 1 game with u at a time'
    # otherwise add a new game to the database
    game = Game(player_uid=args['uid'], moves='', stockfish_elo=args['elo'])
    session.add(game)
    session.commit()
    print(game)
    # report back
    return 'New game successfully started for %s' % args['name']

# make a move for the player
@app.route('/move',methods = ['POST', 'GET'])
def move():
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