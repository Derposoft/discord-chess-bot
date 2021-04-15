from flask import Flask, redirect, url_for, request
app = Flask(__name__)

@app.route('/new')
def new(name):
    # create a new game for the player
   return 'welcome %s' % name

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