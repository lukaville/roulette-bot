import time
import unittest

# Patch async decorator to run async methods sequentially
import telegram.ext.dispatcher as dispatcher
def empty(func):
    return func
dispatcher.run_async = empty

from telegram import Update
from telegram.ext import Updater

from bot import load_modules
from db.mysql_store import MySQLStore
from modules.roulette import RouletteModule
from util.mock_bot import MockBot


class IntegrationTestCase(unittest.TestCase):
    def setUp(self):
        self.store = MySQLStore({
            'MYSQL_HOST': '192.168.99.100',
            'MYSQL_DATABASE': 'roulette_test',
            'MYSQL_USER': 'root',
            'MYSQL_PASSWORD': 'password',
            'MYSQL_CONNECTION_POOL_SIZE': 1
        })

        self.bot = MockBot()
        self.updater = Updater(bot=self.bot)
        load_modules(self.updater.dispatcher, [RouletteModule(self.store)])

    def tearDown(self):
        self.store.drop_db()

    def send_message(self, text, from_user_id=0, skip_answer=True):
        update = {
            'update_id': 0,
            'message': {
                'message_id': 0,
                'text': text,
                'from': {
                    'id': from_user_id,
                    'first_name': 'Jack'
                },
                'date': int(time.time())
            }
        }
        self.updater.dispatcher.processUpdate(Update.de_json(update))

        if skip_answer and len(self.bot.messages) > 0:
            self.bot.pop_message()

    def skip_answer(self):
        self.bot.pop_message()

    def verify_answer(self, answer, to_user_id=None):
        message = self.bot.pop_message()

        if to_user_id:
            self.assertEqual(to_user_id, message['user_id'])

        self.assertEqual(answer, message['text'])
