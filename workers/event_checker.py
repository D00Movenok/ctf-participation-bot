from datetime import datetime

from sqlalchemy import select, update

from common.models import Event, Voter
from common.database import engine
from config import config
import time


class EventChecker:
    conn = engine.connect()

    def start(self):
        while True:
            self.check()
            time.sleep(60)

    def check(self):
        query1 = select(Voter.poll_id)
        res1 = self.conn.execute(query1)
        unique_arr = set()
        for row in res1:
            unique_arr.add(row[0])
        for poll_id in unique_arr:
            query2 = select(Voter).where(Voter.poll_id == poll_id, Voter.will_play == True)
            res2 = self.conn.execute(query2)
            arr = []
            for row in res2:
                arr.append(row)
            if len(arr) >= config['min_will_play']:
                query3 = (update(Event).where(Event.poll_id == poll_id).values(done=True))
                self.conn.execute(query3)
        query4 = (update(Event).where(Event.start_time > datetime.now()).values(done=True))
        self.conn.execute(query4)
