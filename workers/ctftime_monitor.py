import logging
import threading
import time
from datetime import datetime, timezone
from typing import List

import requests
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.orm import SessionTransaction

from actions.telegram import Telegram
from common.database import session
from common.models import Event
from config import config


class CtftimeMonitor:
    _headers = {
        'User-Agent': 'curl/7.68.0'
    }
    _tg_bot = Telegram()

    def start(self):
        for team_id in config['ctf_teams']:
            threading.Thread(target=self.__monitor_cycle,
                             args=(team_id, )).start()

    def __monitor_cycle(self, team_id: int):
        logging.info(f'CTFTime monitoring for team {team_id} starting...')
        while True:
            self.__check_team(team_id)
            time.sleep(60)

    def __check_team(self, team_id: int):
        event_ids = self.__parse_events(self.__get_team_events(team_id))
        if not event_ids:
            return
        with session.begin() as local_session:
            new_event_ids = self.__filter_existing_events(local_session,
                                                          event_ids)
            event_queue = []
            for event_id in new_event_ids:
                logging.info(f'Found new event {event_id} for team {team_id}')
                event = self.__create_event_obj(team_id, event_id)
                self.__create_telegram_poll(event)
                event_queue.append(event)
            local_session.add_all(event_queue)

    def __get_team_events(self, team_id: int) -> str:
        url = f'https://ctftime.org/team/{team_id}'
        resp = requests.get(url, headers=self._headers)
        self.__check_response(resp)
        return resp.text

    def __parse_events(self, content: str) -> List[int]:
        soup = BeautifulSoup(content, 'html.parser')
        events_header = soup.find('h3',
                                  string='Plan to participate in CTF events')
        if not events_header:
            return []
        events_table = events_header.find_next_sibling('table')
        event_links = events_table.find_all('a')
        event_ids = list(map(lambda a: int(a.get('href').split('/')[-1]),
                             event_links))
        return event_ids

    def __filter_existing_events(self, local_session: SessionTransaction,
                                 event_ids: List[int]) -> List[int]:
        query = select(Event.id).where(Event.id.in_(event_ids))
        for existing_event in local_session.execute(query):
            event_ids.remove(existing_event.id)
        return event_ids

    def __create_event_obj(self, team_id: int, event_id: int) -> Event:
        url = f'https://ctftime.org/api/v1/events/{event_id}/'
        resp = requests.get(url, headers=self._headers)
        self.__check_response(resp)
        json = resp.json()
        title = json['title']
        start_time = datetime.fromisoformat(json['start'])
        end_time = datetime.fromisoformat(json['finish'])
        return Event(
            id=event_id,
            team_id=team_id,
            title=title,
            start_time=start_time,
            end_time=end_time,
            done=start_time < datetime.now(timezone.utc),
        )

    def __create_telegram_poll(self, event: Event):
        message = self._tg_bot.create_poll(event)
        event.poll_id = message.poll.id
        if config['tg_pin']:
            self._tg_bot.pin_message(message.chat_id,
                                     message.message_id)
            event.chat_id = message.chat_id
            event.message_id = message.message_id
            event.pinned = True

    def __check_response(self, response: requests.Response):
        if response.status_code != 200 or \
           'Why do I have to complete a CAPTCHA?' in response.text:
            logging.error(
                f'Something wrong, response status code: '
                f'{response.status_code}\n{response.text}'
            )
