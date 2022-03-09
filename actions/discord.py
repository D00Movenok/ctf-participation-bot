import logging

import requests

from common.models import Event
from config import config


class Discord():
    def __init__(self):
        self.token = config['ds_token']
        self.guild_id = config['ds_srv_id']

    def __create(self, type: str, name: str, parent_id: int = None) -> dict:
        if type == 'category':
            pos = config['ds_ins_position']
            json_request = {'name': name, 'type': 4, 'position': pos}
        elif type == 'text':
            json_request = {'name': name, 'type': 0, 'parent_id': parent_id}
        elif type == 'voice':
            json_request = {'name': name, 'type': 2, 'parent_id': parent_id}
        else:
            logging.error(f'Unknown discord type: {type}')
            raise ValueError(f'Unknown discord type: {type}')

        res = requests.post(
            f'https://discord.com/api/v9/guilds/{self.guild_id}/channels',
            json=json_request,
            headers={
                'authorization': f'Bot {self.token}',
            },
        ).json()

        logging.debug(f'Discord api response: {res}')

        if res.get('code', None) == 40001:
            logging.error(
                'Auth error. Check your discord bot token.'
                'Before using bot, you also must connect to and identify '
                'with a gateway at least once. You may use this: '
                'https://github.com/D00Movenok/ctf-participation-bot/blob/'
                'main/static/gateway.html'
            )
            raise Exception('Discord unauthorized')
        elif res.get('code', None) == 50013:
            logging.error('Missing discord bot permissions')
            raise Exception('Missing discord bot permissions')

        return res

    def create_event(self, event: Event):
        logging.info(f'Creating discord event {event.title}...')

        text_channels = ['general'] + config['ds_text_channels']
        voice_channels = config['ds_voice_channels']

        logging.debug(f'Creating category for event {event.title}...')
        category_info = self.__create('category', event.title)
        category_id = category_info['id']

        for channel in text_channels:
            logging.debug(f'Creating text channel {channel} '
                          f'for event {event.title}...')
            self.__create('text', channel, category_id)

        for channel in voice_channels:
            logging.debug(f'Creating voice channel {channel} '
                          f'for event {event.title}...')
            self.__create('voice', channel, category_id)
