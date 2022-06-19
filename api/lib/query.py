from .db.database import GameArchive, init as init_db, db_session, Participant, Game
from sqlalchemy import or_
import logging

from .constants import STOCKFISH_INVITEE_ID

logger = logging.getLogger(__name__)


def init(dbURL, echo):
    init_db(dbURL, echo)


def get_create_participant(discordID):
    db = db_session()
    try:
        participant = _get_participant_with_session(db, discordID)
        if participant == None:
            participant = create_participant(discordID, None)

        return participant
    finally:
        db.close()


def get_participant(discordID):
    # discordID could either be the discord user ID or
    # the GuildMemberID
    db = db_session()
    try:
        return _get_participant_with_session(db, discordID)
    finally:
        db.close()


def _get_participant_with_session(db, discordID):
    return (
        db.query(Participant)
        .filter(
            or_(
                Participant.discord_user_id == discordID,
                Participant.discord_guild_id == discordID,
            )
        )
        .order_by(Participant.id.desc())
        .first()
    )


def get_participant_from_id(db_id):
    db = db_session()
    try:
        return db.query(Participant).filter_by(id=db_id).first()
    finally:
        db.close()


def create_participant(user_id, guild_id):
    db = db_session()
    try:
        return _create_participant_with_session(db, user_id, guild_id)
    finally:
        db.close()


def _create_participant_with_session(db, user_id, guild_id):
    try:
        p = Participant(discord_user_id=user_id, discord_guild_id=guild_id)
        db.add(p)
        db.commit()
        db.refresh(p)
        return p
    except:
        db.rollback()
        return None


def update_participant(user_id, guild_id):
    db = db_session()
    try:
        user = _get_participant_with_session(db, user_id)
        user.guild_id = guild_id
        db.commit()
        return True
    except:
        db.rollback()
        return False
    finally:
        db.close()


def get_recent_game(participant):
    db = db_session()
    try:
        return (
            db.query(Game)
            .filter(
                or_(Game.author_id == participant.id, Game.invitee_id == participant.id)
            )
            .order_by(Game.last_updated.desc())
            .first()
        )
    finally:
        db.close()


def get_solo_game(participant):
    db = db_session()
    try:
        return (
            db.query(Game)
            .filter_by(author_id=participant.id)
            .filter_by(invitee_id=STOCKFISH_INVITEE_ID)
            .first()
        )
    finally:
        db.close()


def get_pvp_game(participant, invitee):
    db = db_session()
    try:
        return (
            db.query(Game)
            .filter_by(author_id=participant.id)
            .filter_by(invitee_id=invitee.id)
            .first()
        )
    finally:
        db.close()


def get_moves_string(game):
    return game.moves


def create_solo_game(author, elo, player_is_white):
    db = db_session()
    try:
        game = Game(
            author_id=author.id,
            invitee_id=STOCKFISH_INVITEE_ID,
            stockfish_elo=elo,
            author_is_white=player_is_white,
            white_to_move=True,
        )
        db.add(game)
        db.commit()
        return True
    except:
        db.rollback()
        return False
    finally:
        db.close()


def create_pvp_game(author, invitee, author_is_white):
    db = db_session()
    try:
        game = Game(
            author_id=author.id,
            invitee_id=invitee.id,
            stockfish_elo=None,
            author_is_white=author_is_white,
            white_to_move=True,
        )
        db.add(game)
        db.commit()
        return True
    except:
        db.rollback()
        return False
    finally:
        db.close()


# BUG make this a stored-procedure/transaction to eliminate data race (2 turns in a row)
def add_move_to_game(game, move):
    delim = ""
    if len(game.moves) > 0:
        delim = " "

    db = db_session()
    try:
        game.moves += delim + move
        game.white_to_move = not game.white_to_move

        # https://docs.sqlalchemy.org/en/14/glossary.html#term-detached
        # https://docs.sqlalchemy.org/en/14/orm/session_api.html?highlight=make_transient#sqlalchemy.orm.Session.merge
        db.merge(game)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Issue with Merging Game: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def archive_game(game):
    db = db_session()
    try:
        game_archive = GameArchive(
            author_id=game.author_id,
            invitee_id=game.invitee_id,
            stockfish_elo=game.stockfish_elo,
            author_is_white=game.author_is_white,
            moves=game.moves,
        )

        db.add(game_archive)
        db.delete(game)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Issue with Archiving Game: {e}")
        db.rollback()
        return False
    finally:
        db.close()
