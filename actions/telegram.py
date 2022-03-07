import logging
from datetime import datetime

import pytz
from telegram import Bot, Message

from common.models import Event
from config import config


class Telegram:
    def __init__(self):
        token = config['tg_token']
        self.bot = Bot(token)

    def __get_time_str(self, date: datetime) -> str:
        timezone_str = config['timezone']
        timezone = pytz.timezone(timezone_str)
        datetime_format = '%a, %d %B %Y, %H:%M %Z'
        return date.astimezone(timezone).\
            strftime(datetime_format)

    def pin_message(self, chat_id: int, message_id: int):
        logging.info(f'Pinning telegram poll...')
        self.bot.pin_chat_message(chat_id, message_id)

    def unpin_message(self, chat_id: int, message_id: int):
        logging.info(f'Unpinning telegram poll...')
        self.bot.unpin_chat_message(chat_id, message_id)

    def create_poll(self, event: Event) -> Message:
        logging.info(f'Creating telegram poll for {event.title}...')
        chat_id = config['tg_chat_id']
        start = self.__get_time_str(event.start_time)
        end = self.__get_time_str(event.end_time)
        message = self.bot.send_poll(
            chat_id,
            f'{event.title}\n'
            f'https://ctftime.org/event/{event.id}\n'
            f'{start} — {end}',
            [
                'will',
                'won\'t',
            ],
            is_anonymous=False,
        )
        return message
