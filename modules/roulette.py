import logging
import random

from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.error import Unauthorized
from telegram.ext import CommandHandler, MessageHandler
from telegram.ext.dispatcher import run_async

from db.mysql_store import STATE_IDLE, STATE_SEARCH
from i18n import _
from resend import USER_MESSAGE_FILTERS, resend_message

logger = logging.getLogger(__name__)

# Default keyboard markup with one button
KEYBOARD_MARKUP = ReplyKeyboardMarkup(one_time_keyboard=True, keyboard=[[
    KeyboardButton(
        text="/roulette"
    )
]])


def format_message(original_text):
    """
    Format original message text from user (adds header)
    :return: formatted original_text
    """
    return _('MESSAGE_BODY') % original_text


class RouletteModule(object):
    def __init__(self, store, analytics):
        self.handlers = [
            CommandHandler('start', self.start_command),
            CommandHandler('help', self.help_command),
            CommandHandler('roulette', self.roulette_command),
            CommandHandler('disconnect', self.disconnect_command),
            MessageHandler([f for f, s in USER_MESSAGE_FILTERS], self.message)
        ]

        self.store = store
        self.analytics = analytics

    @run_async
    def roulette_command(self, bot, update):
        user_id = update.message.from_user.id
        user = self.store.get_user(user_id)

        self.analytics.track(user_id, update.message.to_dict(), 'roulette_command')

        if user is None:
            user = self.store.create_user(user_id)

        if user['chat_with'] and user['chat_with'] > 0:
            paired_user_id = user['chat_with']
            self.store.disconnect(user_id, paired_user_id)
            bot.sendMessage(user_id, text=_('DISCONNECTED_SEARCH_NEW'), reply_markup=KEYBOARD_MARKUP)
            bot.sendMessage(paired_user_id, text=_('DISCONNECTED'), reply_markup=KEYBOARD_MARKUP)

        paired_user_id = self.store.pair_user(user_id, lambda users: random.choice(users))

        if paired_user_id is None:
            bot.sendMessage(user_id, text=_('SEARCHING'), reply_markup=KEYBOARD_MARKUP)
        else:
            logger.info('Paired ' + str(update.message.from_user) + ' with ' + str(paired_user_id))
            bot.sendMessage(user_id, text=_('ESTABLISHED'), reply_markup=KEYBOARD_MARKUP)
            bot.sendMessage(paired_user_id, text=_('ESTABLISHED'), reply_markup=KEYBOARD_MARKUP)

    @run_async
    def message(self, bot, update):
        user_id = update.message.from_user.id

        user = self.store.get_user(user_id)
        if user:
            paired_user_id = user['chat_with']

            if paired_user_id == STATE_SEARCH:
                self.analytics.track(user_id, update.message.to_dict(), 'error_search')
                bot.sendMessage(user_id, text=_('ERROR_SEARCHING'), reply_markup=KEYBOARD_MARKUP)

            if paired_user_id == STATE_IDLE:
                self.analytics.track(user_id, update.message.to_dict(), 'error_idle')
                bot.sendMessage(user_id, text=_('ERROR_IDLE'), reply_markup=KEYBOARD_MARKUP)

            if paired_user_id and paired_user_id > 0:
                logger.info('Resending ' + str(update.message))
                self.analytics.track(user_id, update.message.to_dict(), 'message')
                try:
                    resend_message(bot, update.message, paired_user_id, format_message)
                except Unauthorized:
                    bot.sendMessage(user_id, text=_('DISCONNECTED'), reply_markup=KEYBOARD_MARKUP)
                    self.store.disconnect(user_id, None)
                    self.store.disconnect(paired_user_id, None)

    @run_async
    def disconnect_command(self, bot, update):
        user_id = update.message.from_user.id
        self.analytics.track(user_id, update.message.to_dict(), 'disconnect_command')

        user = self.store.get_user(user_id)

        if user:
            bot.sendMessage(user_id, text=_('DISCONNECTED'), reply_markup=KEYBOARD_MARKUP)
            self.store.disconnect(user_id, None)

            paired_user_id = user['chat_with']
            if paired_user_id and paired_user_id > 0:
                self.store.disconnect(paired_user_id, None)
                bot.sendMessage(paired_user_id, text=_('DISCONNECTED'), reply_markup=KEYBOARD_MARKUP)

    @run_async
    def help_command(self, bot, update):
        user_id = update.message.from_user.id
        bot.sendMessage(user_id, text=_('HELP'))
        self.analytics.track(user_id, update.message.to_dict(), 'help_command')

    @run_async
    def start_command(self, bot, update):
        user_id = update.message.from_user.id
        bot.sendMessage(user_id, text=_('START'), reply_markup=KEYBOARD_MARKUP)
        self.analytics.track(user_id, update.message.to_dict(), 'start_command')

    def get_handlers(self):
        return self.handlers
