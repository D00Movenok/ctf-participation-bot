from sqlalchemy import Column, DateTime, Integer, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Event(Base):
    __tablename__ = 'event'

    team_id = Column(Integer, primary_key=True)
    event_id = Column(Integer, primary_key=True)
    poll_id = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)

    done = Column(Boolean)
