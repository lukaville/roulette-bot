#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Chat with random users telegram bot

import logging
import os

from telegram.ext import Updater

from botan import BotanAnalytics
from config import config
from db.mysql_store import MySQLStore
from modules.roulette import RouletteModule

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def error(bot, update, err):
    logger.warn('Update "%s" caused error "%s"' % (update, err))


def load_modules(dispatcher, modules):
    """
    Add handlers from modules to dispatcher
    :param dispatcher: telegram dispatcher
    :param modules: bot modules
    """
    for module in modules:
        for handler in module.get_handlers():
            dispatcher.add_handler(handler)


def main():
    token = config['TELEGRAM_TOKEN']

    if token is None:
        raise RuntimeError("You must specify TELEGRAM_TOKEN environment variable")

    store = MySQLStore(config)
    analytics = BotanAnalytics(config['BOTAN_TOKEN'])

    updater = Updater(os.getenv('TELEGRAM_TOKEN'))

    dp = updater.dispatcher
    load_modules(dp, [RouletteModule(store, analytics)])

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
