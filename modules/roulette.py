from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters

from db.mysql_store import STATE_IDLE, STATE_SEARCH
from i18n import _

KEYBOARD_MARKUP = ReplyKeyboardMarkup(one_time_keyboard=True, keyboard=[[
    KeyboardButton(
        text="/roulette"
    )
]])


def help_command(bot, update):
    bot.sendMessage(update.message.chat_id,
                    text=_('HELP'))


def start_command(bot, update):
    bot.sendMessage(update.message.chat_id,
                    text=_('START'),
                    reply_markup=KEYBOARD_MARKUP)


def format_message(original_message):
    return _('MESSAGE_BODY') % original_message.text


class RouletteModule(object):
    def __init__(self, store):
        self.handlers = [
            CommandHandler('start', start_command),
            CommandHandler('help', help_command),
            CommandHandler('roulette', self.roulette_command),
            MessageHandler([Filters.text], self.message)
        ]

        self.store = store

    def roulette_command(self, bot, update):
        user_id = update.message.from_user.id
        user = self.store.get_user(user_id)

        if user is None:
            user = self.store.create_user(user_id)

        if user['chat_with'] and user['chat_with'] > 0:
            paired_user_id = user['chat_with']
            self.store.disconnect(user_id, paired_user_id)
            bot.sendMessage(user_id,
                            text=_('DISCONNECTED_SEARCH_NEW'),
                            reply_markup=KEYBOARD_MARKUP)
            bot.sendMessage(paired_user_id,
                            text=_('DISCONNECTED'),
                            reply_markup=KEYBOARD_MARKUP)

        paired_user_id = self.store.roulette(user_id)

        if paired_user_id is None:
            bot.sendMessage(user_id,
                            text=_('SEARCHING'),
                            reply_markup=KEYBOARD_MARKUP)
        else:
            bot.sendMessage(user_id,
                            text=_('ESTABLISHED'),
                            reply_markup=KEYBOARD_MARKUP)
            bot.sendMessage(paired_user_id,
                            text=_('ESTABLISHED'),
                            reply_markup=KEYBOARD_MARKUP)

    def message(self, bot, update):
        user_id = update.message.from_user.id

        user = self.store.get_user(user_id)
        if user:
            paired_user_id = user['chat_with']

            if paired_user_id == STATE_SEARCH:
                bot.sendMessage(user_id,
                                text=_('ERROR_SEARCHING'),
                                reply_markup=KEYBOARD_MARKUP)

            if paired_user_id == STATE_IDLE:
                bot.sendMessage(user_id,
                                text=_('ERROR_IDLE'),
                                reply_markup=KEYBOARD_MARKUP)

            if paired_user_id and paired_user_id > 0:
                message = format_message(update.message)
                bot.sendMessage(paired_user_id,
                                text=message,
                                reply_markup=KEYBOARD_MARKUP)

    def get_handlers(self):
        return self.handlers
