from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters

from db.mysql_store import STATE_IDLE, STATE_SEARCH

KEYBOARD_MARKUP = ReplyKeyboardMarkup(one_time_keyboard=True, keyboard=[[
    KeyboardButton(
        text="/roulette"
    )
]])


def help_command(bot, update):
    bot.sendMessage(update.message.chat_id,
                    text="Help!")


def start_command(bot, update):
    bot.sendMessage(update.message.chat_id,
                    text="Start!",
                    reply_markup=KEYBOARD_MARKUP)


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

        if user['chat_with']:
            paired_user_id = user['chat_with']
            self.store.disconnect(user_id, paired_user_id)
            bot.sendMessage(user_id,
                            text="Disconnected, searching new user...",
                            reply_markup=KEYBOARD_MARKUP)
            bot.sendMessage(paired_user_id,
                            text="Disconnected. Use /roulette to connect to new user...",
                            reply_markup=KEYBOARD_MARKUP)

        paired_user_id = self.store.roulette(user_id)

        if paired_user_id is None:
            bot.sendMessage(user_id,
                            text="Searching couple...",
                            reply_markup=KEYBOARD_MARKUP)
        else:
            bot.sendMessage(user_id,
                            text="Connection established with " + str(paired_user_id),
                            reply_markup=KEYBOARD_MARKUP)
            bot.sendMessage(paired_user_id,
                            text="Hi! Connection established with " + str(user_id),
                            reply_markup=KEYBOARD_MARKUP)

    def message(self, bot, update):
        user_id = update.message.from_user.id

        user = self.store.get_user(user_id)
        if user:
            paired_user_id = user['chat_with']

            if paired_user_id == STATE_SEARCH:
                bot.sendMessage(user_id,
                                text='Wait...',
                                reply_markup=KEYBOARD_MARKUP)

            if paired_user_id == STATE_IDLE:
                bot.sendMessage(user_id,
                                text='Send /roulette to connect with new user',
                                reply_markup=KEYBOARD_MARKUP)

            if paired_user_id is not None:
                bot.sendMessage(paired_user_id,
                                text=update.message.text,
                                reply_markup=KEYBOARD_MARKUP)

    def get_handlers(self):
        return self.handlers
