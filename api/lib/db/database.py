from sqlalchemy import create_engine
from sqlalchemy.sql import func as sqlfunc
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    TIMESTAMP,
    ForeignKeyConstraint,
    UniqueConstraint,
    CheckConstraint,
    Text,
)

Base = declarative_base()
Session = None


def init(dbURI, echo):
    # I don't think Engine will be garbage collected since we
    #    bind it to Session global variable. Engine should still have a reference
    engine = create_engine(dbURI, echo=echo, connect_args={"check_same_thread": False})

    global Session
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)


def db_session():
    if Session is None:
        raise RuntimeError("DB Session Was never initialized!")

    return Session()


class Participant(Base):
    __tablename__ = "participant"

    id = Column(Integer, primary_key=True, autoincrement=True)
    discord_user_id = Column(String, unique=True)
    discord_guild_id = Column(String, unique=True)
    last_updated = Column(
        TIMESTAMP,
        nullable=False,
        server_default=sqlfunc.current_timestamp(),
        server_onupdate=text(f" ON UPDATE {sqlfunc.current_timestamp()}"),
    )


# BUG One could create 2 games per duo by inviting eachother to their own game
class Game(Base):
    __tablename__ = "chess_game"

    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, nullable=False, index=True)
    invitee_id = Column(Integer, nullable=False, index=True)  # -1 for stockfish games
    stockfish_elo = Column(Integer)  # NULL for competetive Games
    author_is_white = Column(Boolean, nullable=False)
    white_to_move = Column(Boolean, nullable=False, default=True)
    moves = Column(Text, nullable=False, default="")
    last_updated = Column(
        TIMESTAMP,
        nullable=False,
        index=True,
        server_default=sqlfunc.current_timestamp(),
        server_onupdate=text(f" ON UPDATE {sqlfunc.current_timestamp()}"),
    )
    ForeignKeyConstraint(["author_id"], ["Participant.id"], name="FK_AUTHOR_PVP")
    UniqueConstraint("author_id", "invitee_id", name="UK_AUTHOR_INVITEE")
    CheckConstraint("author_id <> invitee_id", name="CHCK_NO_SELF")


# Create a table with no constraints to move the game once complete
class GameArchive(Base):
    __tablename__ = "chess_game_archive"

    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, nullable=False, index=True)
    invitee_id = Column(Integer, nullable=False, index=True)  # -1 for stockfish games
    stockfish_elo = Column(Integer)  # NULL for competetive Games
    author_is_white = Column(Boolean, nullable=False)
    moves = Column(Text, nullable=False)
    last_updated = Column(
        TIMESTAMP,
        nullable=False,
        server_default=sqlfunc.current_timestamp(),
        server_onupdate=text(f" ON UPDATE {sqlfunc.current_timestamp()}"),
    )
