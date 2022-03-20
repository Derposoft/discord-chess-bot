from db.database import GameArchive, init as init_db
from db.database import db_session, GameLegacy,\
    Participant, Game, Move

from constants import STOCKFISH_INVITEE_ID

def init(dbURL):
    init_db(dbURL)

def get_participant(discordID):
    # discordID could either be the discord user ID or 
    # the GuildMemberID
    db = db_session()
    _get_participant_with_session(db, discordID)

def _get_participant_with_session(db, discordID):
    return db.query(Participant).\
        filter(Participant.discord_user_id == discordID or Participant.discord_guild_id == discordID).\
        order_by(Participant.id.desc()).\
        first()

def get_participant_from_id(db_id):
    db = db_session()
    return db.query(Participant).filter_by(id=db_id).first()

def create_participant(user_id, guild_id):
    try:
        db = db_session()
        p = Participant(user_id = user_id, guild_id = guild_id)
        db.add(p)
        db.commit()
        return True
    except:
        db.rollback()
        return False

def update_participant(user_id, guild_id):
    try:
        db = db_session()
        user = _get_participant_with_session(db, user_id)
        user.guild_id = guild_id
        db.commit()
        return True
    except:
        db.rollback()
        return False
        

def get_recent_game(participant):
    db = db_session()
    return db.query(Game).\
        filter(Game.author_id == participant.id or Game.invitee_id == participant.id).\
        order_by(Game.id.desc()).\
        first()

def get_solo_game(participant):
    db = db_session()
    return db.query(Game).\
        filter_by(participant_id=participant.id).\
        filter_by(invitee_id=STOCKFISH_INVITEE_ID).\
        first()

def get_pvp_game(participant, invitee):
    db = db_session()
    return db.query(Game).\
        filter_by(participant_id=participant.id).\
        filter_by(invitee_id=invitee.id).\
        first()

def get_moves_string(game):
    db = db_session()
    _get_moves_string_with_session(db, game)

def _get_moves_string_with_session(db, game):
    moves = db.query(Move).\
            filter_by(game_id=game.id).\
            all()

    builder = ""
    for move in moves:
        builder += move
    
    return builder

def create_solo_game(participant, elo, player_is_white):
    try:
        db = db_session()
        game = Game(participant_id = participant.id, invitee_id = STOCKFISH_INVITEE_ID, stockfish_elo = elo, author_is_white = player_is_white)
        db.add(game)
        db.commit()
        return True
    except:
        db.rollback()
        return False

def create_pvp_game(author, invitee, author_is_white):
    try:
        db = db_session()
        game = Game(author_id = author.id, invitee_id = invitee.id, stockfish_elo = None, author_is_white = author_is_white)
        db.add(game)
        db.commit()
        return True
    except:
        db.rollback()
        return False

# BUG make this a stored-procedure/transaction to eliminate data race (2 turns in a row)
def add_move_to_game(game, move, isWhiteMove):
    try:
        db = db_session()
        move_row = Move(game_id = game.id, move = move, white_move = isWhiteMove)
        db.add(move_row)
        db.commit()
        return True
    except:
        db.rollback()
        return False

def check_users_turn(game, mover):
    db = db_session()
    last_move = db.query(Move).\
                filter_by(game_id=game.id).\
                order_by(Move.id.desc()).\
                first()
    mover_is_author = game.author_id == mover.id
    author_is_white = game.author_is_white
    its_whites_turn = not last_move.white_move

    return (author_is_white == its_whites_turn) == mover_is_author

def archive_game(game):
    try:
        db = db_session()

        game_archive = GameArchive(
            author_id = game.author_id, 
            invitee_id = game.invitee_id, 
            stockfish_elo = game.stockfish_elo,
            author_is_white = game.author_is_white,
            moves = _get_moves_string_with_session(db, game)
            )
        
        db.add(game_archive)
        db.delete(game)
    except:
        db.rollback()
        return False