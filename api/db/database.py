from sqlalchemy import create_engine
from sqlalchemy.sql import func as sqlfunc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP

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

class GameLegacy(Base):
    __tablename__ = 'games'

    uid = Column(String, primary_key=True, unique=True)
    moves = Column(String)
    stockfish_elo = Column(Integer)
    player_side = Column(String)

class StockfishGame(Base):
    __tablename__ = 'stockfish_game'

    id=Column(Integer, primary_key=True, autoincrement=True)
    participant_id = Column(unique=True)
    moves_id=Column(Integer)
    next_move=Column(Boolean)
    stockfish_elo = Column(Integer)
    player_side = Column(String)
    last_updated=Column(TIMESTAMP, nullable=False, server_default=sqlfunc.current_timestamp())
    
