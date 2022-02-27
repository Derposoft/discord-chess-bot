from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer

engine = create_engine(
    'sqlite:///storage.db',
    echo=True,
    connect_args={'check_same_thread': False}
)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def db_session():
    return Session()

class Game(Base):
    __tablename__ = 'games'

    uid = Column(String, primary_key=True, unique=True)
    moves = Column(String)
    stockfish_elo = Column(Integer)
    player_side = Column(String)
    
Base.metadata.create_all(engine)