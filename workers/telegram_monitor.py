from sqlalchemy import insert
from telegram import Update
from telegram.ext import Updater, PollAnswerHandler, CallbackContext

from common.database import session
from common.models import Voter
from config import config


class TelegramMonitor:
    token = config['tg_token']
    updater = Updater(token)
    dispatcher = updater.dispatcher


    def start(self):
        self.dispatcher.add_handler(PollAnswerHandler(self.monitor_poll_answer))
        self.updater.start_polling()

    def monitor_poll_answer(self, update: Update, context: CallbackContext):
        answer = update.poll_answer
        poll_id = answer.poll_id
        user_id = answer.user.id
        option = answer.option_ids[0]
        query = insert(Voter).values(user_id=user_id, poll_id=poll_id, will_play=(True if option == 0 else False))
        with session.begin() as local_session:
            local_session.execute(query)
