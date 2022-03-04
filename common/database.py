from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///database.db')

session = sessionmaker(
    engine, expire_on_commit=False,
)
