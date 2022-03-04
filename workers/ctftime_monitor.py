import logging
import threading
import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup
from sqlalchemy import select

from actions.telegram_create import create_telegram_poll
from common.database import session
from common.models import Event
from config import config


class CtftimeMonitor:
    _headers = {
        'User-Agent': 'curl/7.68.0'
    }

    def start(self):
        for team_id in config['ctf_teams']:
            threading.Thread(target=self.__monitor_cycle,
                             args=(team_id, )).start()

    def __monitor_cycle(self, team_id):
        logging.info(f'CTFTime monitoring for team {team_id} starting...')
        while True:
            self.__check_team(team_id)
            time.sleep(60)

    def __check_team(self, team_id):
        event_ids = self.__parse_events(self.__get_team_events(team_id))
        if not event_ids:
            return
        with session.begin() as local_session:
            new_event_ids = self.__filter_existing_events(local_session,
                                                          event_ids)
            event_queue = []
            for event_id in new_event_ids:
                logging.info(f'Found new event {event_id} for team {team_id}')
                event_queue.append(self.__create_event_obj(team_id, event_id))
                event_queue[-1].poll_id = create_telegram_poll(event_queue[-1])
            local_session.add_all(event_queue)

    def __get_team_events(self, team_id):
        url = f'https://ctftime.org/team/{team_id}'
        resp = requests.get(url, headers=self._headers)
        self.__check_response(resp)
        return resp.text

    def __parse_events(self, content):
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

    def __filter_existing_events(self, local_session, event_ids):
        query = select(Event.id).where(Event.id.in_(event_ids))
        for existing_event in local_session.execute(query):
            event_ids.remove(existing_event.id)
        return event_ids

    def __create_event_obj(self, team_id, event_id):
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

    def __check_response(self, response):
        if response.status_code != 200 or \
           'Why do I have to complete a CAPTCHA?' in response.text:
            logging.error(
                f'Something wrong, response status code: '
                f'{response.status_code}\n{response.text}'
            )
