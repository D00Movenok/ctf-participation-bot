import logging
import requests


def create(type, name, bot_token, guild_id, parent_id = None):
    if type == 'category':
        json_request = {'name': name, 'type': 4}
    if type == 'text':
        json_request = {'name': name, 'type': 0, 'parent_id': parent_id}
    if type == 'voice':
        json_request = {'name': name, 'type': 2, 'parent_id': parent_id}

    res = requests.post(f'https://discord.com/api/v9/guilds/{guild_id}/channels', json=json_request,
                        headers={'authorization': f'Bot {bot_token}', 'Content-Type': 'application/json'})
    return res.json()


def create_discord_channels(config):
    bot_token = config['ds_token']
    guild_id = config['ds_srv_id']
    text_channels = config['text_channels']
    voice_channels = config['voice_channels']

    category_info = create('category', 'event', bot_token, guild_id)
    category_id = category_info['id']
    category_name = category_info['name']
    logging.info(f'Created category {category_name} for event with id {category_id}')

    for channel in text_channels:
        create('text', channel, bot_token, guild_id, category_id)
        logging.info(f'Created text channel {channel} for event in category {category_name}')

    for channel in voice_channels:
        create('voice', channel, bot_token, guild_id, category_id)
        logging.info(f'Created voice channel {channel} for event in category {category_name}')
