import logging

from common.database import engine
from common.models import Base
from config import config
from workers import CtftimeMonitor, EventChecker, TelegramMonitor


def main():
    if config['DEBUG']:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(levelname)s[%(asctime)s] %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)
        logging.getLogger("sqlalchemy.pool").setLevel(logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO,
                            format='%(levelname)s[%(asctime)s] %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')

    Base.metadata.create_all(engine)

    CtftimeMonitor().start()
    TelegramMonitor().start()
    EventChecker().start()


if __name__ == '__main__':
    main()
