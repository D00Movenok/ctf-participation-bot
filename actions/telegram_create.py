from datetime import datetime

import pytz
from telegram import Bot

from common.models import Event
from config import config


def get_time_str(date: datetime) -> str:
    timezone_str = config['timezone']
    timezone = pytz.timezone(timezone_str)
    datetime_format = '%a, %d %B %Y, %H:%M %Z'
    return date.astimezone(timezone).\
        strftime(datetime_format)


def create_telegram_poll(event: Event) -> int:
    token = config['tg_token']
    chat_id = config['tg_chat_id']
    bot = Bot(token)

    start = get_time_str(event.start_time)
    end = get_time_str(event.end_time)

    message = bot.send_poll(
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

    return message.poll.id
