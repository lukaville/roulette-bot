import random

from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler
from telegram.ext.dispatcher import run_async

from db.mysql_store import STATE_IDLE, STATE_SEARCH
from i18n import _

# Default keyboard markup with one button
from resend import USER_MESSAGE_FILTERS, resend_message

KEYBOARD_MARKUP = ReplyKeyboardMarkup(one_time_keyboard=True, keyboard=[[
    KeyboardButton(
        text="/roulette"
    )
]])


@run_async
def help_command(bot, update):
    bot.sendMessage(update.message.from_user.id, text=_('HELP'))


@run_async
def start_command(bot, update):
    bot.sendMessage(update.message.from_user.id, text=_('START'), reply_markup=KEYBOARD_MARKUP)


def format_message(original_text):
    """
    Format original message text from user (adds header)
    :return: formatted original_text
    """
    return _('MESSAGE_BODY') % original_text


class RouletteModule(object):
    def __init__(self, store):
        self.handlers = [
            CommandHandler('start', start_command),
            CommandHandler('help', help_command),
            CommandHandler('roulette', self.roulette_command),
            MessageHandler([f for f, s in USER_MESSAGE_FILTERS], self.message)
        ]

        self.store = store

    @run_async
    def roulette_command(self, bot, update):
        user_id = update.message.from_user.id
        user = self.store.get_user(user_id)

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
            bot.sendMessage(user_id, text=_('ESTABLISHED'), reply_markup=KEYBOARD_MARKUP)
            bot.sendMessage(paired_user_id, text=_('ESTABLISHED'), reply_markup=KEYBOARD_MARKUP)

    @run_async
    def message(self, bot, update):
        user_id = update.message.from_user.id

        user = self.store.get_user(user_id)
        if user:
            paired_user_id = user['chat_with']

            if paired_user_id == STATE_SEARCH:
                bot.sendMessage(user_id, text=_('ERROR_SEARCHING'), reply_markup=KEYBOARD_MARKUP)

            if paired_user_id == STATE_IDLE:
                bot.sendMessage(user_id, text=_('ERROR_IDLE'), reply_markup=KEYBOARD_MARKUP)

            if paired_user_id and paired_user_id > 0:
                resend_message(bot, update.message, paired_user_id, format_message,
                               reply_markup=KEYBOARD_MARKUP)

    def get_handlers(self):
        return self.handlers
