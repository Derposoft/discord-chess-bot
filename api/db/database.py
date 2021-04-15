from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session as DatabaseSession
from storage.models import Base
import config

engine = create_engine(
    config.database_url,
    echo=True,
    connect_args={'check_same_thread': False}
)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def db_session():
    s: DatabaseSession = Session()
    try:
        yield s
    except:
        s.rollback()
    finally:
        s.close()