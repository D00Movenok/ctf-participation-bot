import threading
from datetime import datetime, timedelta

from sqlalchemy import select, update

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
        with session.begin() as local_session:
            query = select(Voter.poll_id)
            result = local_session.execute(query)
            unique_arr = set()
            for row in result:
                unique_arr.add(row[0])
            for poll_id in unique_arr:
                query = select(Voter).where(Voter.poll_id == poll_id, Voter.will_play == True)
                result = local_session.execute(query)
                arr = []
                for row in result:
                    arr.append(row)
                if len(arr) >= config['min_will_play']:
                    query = (update(Event).where(Event.poll_id == poll_id).values(done=True))
                    local_session.execute(query)
                    query = select(Event).where(Event.poll_id == poll_id)
                    create_discord_channels(local_session.execute(query))
            query = (update(Event).where(Event.start_time < (datetime.now() + timedelta(days=1))).values(done=True))
            local_session.execute(query)
