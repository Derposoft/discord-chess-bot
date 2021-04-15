from typing import Optional
from pydantic import BaseModel, validator
from sqlalchemy import Column, String, Integer
from db.database import Base

class Game(Base):
    __tablename__ = 'games'

    uid = Column(String, primary_key=True)
    moves = Column(String)
    stockfish_elo = Column(Integer)