config = {
    # Telegram API token
    'tg_token': '',
    # Telegram chat ID
    'tg_chat_id': 123,
    # The lowest acceptable amount of people to participate in an event
    'min_will_play': 4,

    # Discord API token
    'ds_token': '',
    # Discord server ID
    'ds_srv_id': 123,
    # New category insertion position
    # [0; +inf)
    # 0 is the highest
    'ds_ins_position': 0,
    # The names of the text channels you want to generate
    # 'general' will be created automatically
    'ds_text_channels': [
        'web', 'rev', 'forensics',
    ],
    # The names of the voice channels you want to generate
    'ds_voice_channels': [
        'web', 'rev', 'forensics',
    ],

    # IDs of your teams on CTFTime
    'ctf_teams': [
        1,2,3
    ],

    # For dates in poll
    'timezone': 'Europe/Moscow',

    # Enables DEBUG logging
    'DEBUG': False,
}
