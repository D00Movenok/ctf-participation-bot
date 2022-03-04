import logging

import requests

from common.models import Event
from config import config


def create(type, name, bot_token, guild_id, parent_id=None):
    if type == 'category':
        json_request = {'name': name, 'type': 4}
    elif type == 'text':
        json_request = {'name': name, 'type': 0, 'parent_id': parent_id}
    elif type == 'voice':
        json_request = {'name': name, 'type': 2, 'parent_id': parent_id}
    else:
        logging.error(f'Unknown discord type: {type}')
        raise ValueError(f'Unknown discord type: {type}')

    res = requests.post(
        f'https://discord.com/api/v9/guilds/{guild_id}/channels',
        json=json_request,
        headers={
            'authorization': f'Bot {bot_token}',
        },
    ).json()

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


def create_discord_channels(event: Event):
    logging.info(f'Creating discord event {event.id}...')

    bot_token = config['ds_token']
    guild_id = config['ds_srv_id']
    text_channels = config['text_channels']
    voice_channels = config['voice_channels']

    logging.debug(f'Creating category for event {event.id}...')
    category_info = create('category', event.title, bot_token, guild_id)
    category_id = category_info['id']

    for channel in text_channels:
        logging.debug(f'Creating text channel {channel} '
                      f'for event {event.id}...')
        create('text', channel, bot_token, guild_id, category_id)

    for channel in voice_channels:
        logging.debug(f'Creating voice channel {channel} '
                      f'for event {event.id}...')
        create('voice', channel, bot_token, guild_id, category_id)
