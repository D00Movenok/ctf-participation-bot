import logging

from common.database import engine
from common.models import Base


def main():
    logging.basicConfig(level=logging.INFO)
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    main()
