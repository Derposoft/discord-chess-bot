from typing import Optional
from pydantic import BaseModel, validator
from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Game(Base):
    __tablename__ = 'games'

    player_uid = Column(String, primary_key=True)
    moves = Column(String)
    stockfish_elo = Column(Integer)