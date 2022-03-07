import logging
import threading
import time
from datetime import datetime, timedelta

from sqlalchemy import column, func, select

from actions.discord import Discord
from actions.telegram import Telegram
from common.database import session
from common.models import Event, Voter
from config import config


class EventChecker:
    _tg_bot = Telegram()
    _discord_bot = Discord()

    def start(self):
        threading.Thread(target=self.__monitor_cycle).start()

    def __monitor_cycle(self):
        logging.info('Event checker starting...')
        while True:
            self.__check()
            time.sleep(60)

    def __check(self):
        logging.debug('Сhecking events for readiness...')
        with session.begin() as local_session:
            self.__check_ready(local_session)
            self.__check_started(local_session)

    def __check_ready(self, local_session):
        subquery = select(Voter.poll_id).\
            where(Voter.will_play == True).\
            group_by(Voter.poll_id).\
            having(func.count(Voter.user_id) >= config['min_will_play'])
        query = select(Event).\
            where(
                Event.start_time <= (datetime.now() + timedelta(days=1)),
                column('poll_id').in_(subquery),
                Event.done == False,
            )
        result = local_session.scalars(query)
        for event in result:
            self._discord_bot.create_event(event)
            event.done = True

    def __check_started(self, local_session):
        query = select(Event).\
            where(Event.start_time <= datetime.now())
        result = local_session.scalars(query)
        for event in result:
            if event.message_id is not None and event.chat_id is not None and\
               event.pinned:
                self._tg_bot.unpin_message(event.chat_id, event.message_id)
                event.pinned = False
            event.done = True
