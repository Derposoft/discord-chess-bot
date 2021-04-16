from db.database import Game

def parse_args(request):
    return request.args

def check_in_game(player_uid, db):
    return db.query(Game).filter_by(uid=player_uid).first()

def mention(args):
    return ' @' + args['name'] + ' '