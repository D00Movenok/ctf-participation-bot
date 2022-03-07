from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, primary_key=True)
    poll_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    # additional data for pinning
    chat_id = Column(Integer)
    message_id = Column(Integer)
    pinned = Column(Boolean, default=False)

    done = Column(Boolean, default=False)


class Voter(Base):
    __tablename__ = 'voter'

    user_id = Column(Integer, primary_key=True)
    poll_id = Column(Integer, primary_key=True)
    will_play = Column(Boolean)
