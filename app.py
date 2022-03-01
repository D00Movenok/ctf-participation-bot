import logging

from common.database import engine
from common.models import Base
from workers import CtftimeMonitor


def main():
    logging.basicConfig(level=logging.INFO)
    Base.metadata.create_all(engine)
    CtftimeMonitor().start()


if __name__ == '__main__':
    main()
