from telegram import KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CommandHandler


def help_command(bot, update):
    bot.sendMessage(update.message.chat_id,
                    text="Help!")


def start_command(bot, update):
    buttons = [[
        KeyboardButton(
            text="/roulette"
        )
    ]]

    bot.sendMessage(update.message.chat_id,
                    text="Start!", reply_markup=ReplyKeyboardMarkup(keyboard=buttons, one_time_keyboard=True))


class CommandsModule(object):
    def __init__(self):
        self.handlers = [
            CommandHandler('start', start_command),
            CommandHandler('help', help_command),
        ]

    def get_handlers(self):
        return self.handlers
