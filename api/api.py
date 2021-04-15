from flask import Flask, url_for, request
from stockfish import Stockfish
stockfish = Stockfish('/usr/games/stockfish')
import db.Game as Game
from db.database import db_session
import utils

app = Flask(__name__)

@app.route('/new')
def new():
    # create a new game for the player
    print(request.query_string)
    print(request.args)
    args = utils.parse_args(request)
    return 'New game successfully started for %s' % args["name"]

@app.route('/move',methods = ['POST', 'GET'])
def move():
    # make a move for the player
    return 'under construction'


@app.route('/ff',methods = ['POST', 'GET'])
def ff():
    # accept the player's resignation
    return 'under construction'


@app.route('/cheat',methods = ['POST', 'GET'])
def cheat():
    # allow the player to cheat
    return 'under construction'

if __name__ == '__main__':
   app.run(debug = True)