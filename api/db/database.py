from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer
import config

engine = create_engine(
    config.database_url,
    echo=True,
    connect_args={'check_same_thread': False}
)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def db_session():
    return Session()
    '''s: DatabaseSession = Session()
    try:
        yield s
    except:
        s.rollback()
    finally:
        s.close()'''

class Game(Base):
    __tablename__ = 'games'

    uid = Column(String, primary_key=True)
    moves = Column(String)
    stockfish_elo = Column(Integer)
    player_side = Column(String)
    
Base.metadata.create_all(engine)