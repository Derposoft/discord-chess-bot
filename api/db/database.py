from sqlalchemy import create_engine
from sqlalchemy.sql import func as sqlfunc
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP, ForeignKeyConstraint

Base = declarative_base()
Session = None

def init(dbURI):
    # I don't think Engine should be garbage collected since we
    #    bind it to Session. Engine should still have a refer
    engine = create_engine(
        dbURI,
        echo=True,
        connect_args={'check_same_thread': False}
    )
    
    global Session
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)


def db_session():
    if Session is None:
        raise RuntimeError("DB Session Was never initialized!")

    return Session()

## DEPRECATED
class GameLegacy(Base):
    __tablename__ = 'games'

    # BUG primary keys are automatically unique in most type of SQL.
    uid = Column(String, primary_key=True, unique=True)
    moves = Column(String)
    stockfish_elo = Column(Integer)
    player_side = Column(String)

class Participant(Base):
    __tablename__ = 'participant'

    id=Column(Integer, primary_key=True, autoincrement=True)
    discord_user_id=Column(String, unique=True)
    dicord_guild_id=Column(String)
    last_updated = Column(TIMESTAMP, nullable=False, server_default=sqlfunc.current_timestamp(), server_onupdate=text(f' ON UPDATE {sqlfunc.current_timestamp()}'))

class StockfishGame(Base):
    __tablename__ = 'stockfish_game'

    id=Column(Integer, primary_key=True, autoincrement=True)
    participant_id = Column(Integer, nullable=False, unique=True)
    stockfish_elo = Column(Integer)
    player_is_white = Column(Boolean, nullable=False)
    finished = Column(Boolean, nullable=False, default=False)
    last_updated=Column(TIMESTAMP, nullable=False, server_default=sqlfunc.current_timestamp(), server_onupdate=text(f' ON UPDATE {sqlfunc.current_timestamp()}'))
    ForeignKeyConstraint(['participant_id'], ['Participant.id'], name='FK_Participant_Stockfish')

class StockfishMoves(Base):
    __tablename__ = 'stockfish_moves'

    id=Column(Integer, primary_key=True, autoincrement=True)
    game_id=Column(Integer)
    move=Column(String, nullable=False)
    white_move=Column(Boolean, nullable=False)
    last_updated = Column(TIMESTAMP, nullable=False, server_default=sqlfunc.current_timestamp(), server_onupdate=text(f' ON UPDATE {sqlfunc.current_timestamp()}'))
    ForeignKeyConstraint(['game_id'], ['StockfishGame.id'], name='FK_MOVE_STOCKFISH')

class CompetitiveGame(Base):
    __tablename__ = 'pvp_game'

    id=Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, nullable=False)
    invitee_id = Column(Integer, nullable=False)
    author_is_white = Column(Boolean, nullable=False)
    finished = Column(Boolean, nullable=False, default=False)
    last_updated = Column(TIMESTAMP, nullable=False, server_default=sqlfunc.current_timestamp(), server_onupdate=text(f' ON UPDATE {sqlfunc.current_timestamp()}'))
    ForeignKeyConstraint(['author_id'], ['Participant.id'], name='FK_AUTHOR_PVP')
    ForeignKeyConstraint(['invitee_id'], ['Participant.id'], name='FK_INVITEE_PVP')

class CompetitiveMoves(Base):
    __tablename__ = 'pvp_moves'

    id=Column(Integer, primary_key=True, autoincrement=True)
    game_id=Column(Integer)
    move=Column(String, nullable=False)
    white_move=Column(Boolean, nullable=False)
    last_updated = Column(TIMESTAMP, nullable=False, server_default=sqlfunc.current_timestamp(), server_onupdate=text(f' ON UPDATE {sqlfunc.current_timestamp()}'))
    ForeignKeyConstraint(['game_id'], ['CompetitiveGame.id'], name='FK_MOVE_PVP')