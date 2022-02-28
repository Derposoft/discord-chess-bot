from db.database import init as init_db
from db.database import db_session, GameLegacy,\
    Participant, StockfishGame, StockfishMoves, CompetitiveGame, CompetitiveMoves

def init(dbURL):
    init_db(dbURL)

def get_participant(discordID):
    # discordID could either be the discord user ID or 
    # the GuildMemberID
    db = db_session()
    user = db.query(Participant).filter_by(discord_user_id=discordID).first()
    if user != None:
        return user
    
    return db.query(Participant).filter_by(discord_guild_id=discordID).first()

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

def check_in_solo(participant):
    db = db_session()
    return db.query(StockfishGame).\
        filter_by(participant_id=participant.id).\
        filter_by(finished=False).\
        order_by(StockfishGame.id.desc()).\
        first()

def create_stockfish_game(participant, elo, player_is_white):
    try:
        db = db_session()
        game = StockfishGame(participant_id = participant.id, stockfish_elo = elo, player_is_white = player_is_white)
        db.add(game)
        db.commit()
        return True
    except:
        db.rollback()
        return False

def check_in_pvp(author, invitee):
    db = db_session()
    game = db.query(CompetitiveGame).\
        filter_by(author_id = author.id).\
        filter_by(invitee_id = invitee.id).\
        filter_by(finished=False).\
        order_by(CompetitiveGame.id.desc()).\
        first()
    if game != None:
        return game
    return db.query(CompetitiveGame).\
        filter_by(author_id = invitee.id).\
        filter_by(invitee_id = author.id).\
        filter_by(finished=False).\
        order_by(CompetitiveGame.id.desc()).\
        first()

def create_competitive_game(author, invitee, author_is_white):
    try:
        db = db_session()
        game = CompetitiveGame(author_id = author.id, invitee_id = invitee.id, author_is_white = author_is_white)
        db.add(game)
        db.commit()
        return True
    except:
        db.rollback()
        return False

def check_in_pvp(p1_uid, p2_uid, db):
    #print(f'checking {p1_uid},{p2_uid} and {p2_uid},{p1_uid}')
    p12 = f'{p1_uid},{p2_uid}'
    p21 = f'{p2_uid},{p1_uid}'
    p1p2 = db.query(Game).filter_by(uid=p12).first()
    p2p1 = db.query(Game).filter_by(uid=p21).first()
    print("GAMES FOUND", p1p2, p2p1)
    return  p1p2 if p1p2 else p2p1