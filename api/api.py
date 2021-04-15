from flask import Flask, url_for, request
from stockfish import Stockfish
stockfish = Stockfish('/usr/games/stockfish')
import db.Game as Game
from db.database import db_session
import utils

app = Flask(__name__)

# creates a new game for the player
@app.route('/new')
def new():
    args = utils.parse_args(request)
    game = Game(player_uid=args['uid'], moves='', stockfish_elo=args['elo'])
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