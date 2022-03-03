import threading
from datetime import datetime, timedelta

from sqlalchemy import select, update, func, column

from common.models import Event, Voter
from common.database import session
from config import config
from actions.discord_create import create_discord_channels
import time


class EventChecker:
    def start(self):
        threading.Thread(target=self.__monitor_cycle).start()

    def __monitor_cycle(self):
        while True:
            self.check()
            time.sleep(60)

    def check(self):
        print(datetime.now())
        with session.begin() as local_session:
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
            for x in result:
                create_discord_channels(x)
                x.done = True

