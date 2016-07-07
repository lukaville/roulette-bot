from telegram.ext import MessageHandler, Filters
from telegram.ext.dispatcher import run_async


def help_command(bot, update):
    bot.sendMessage(update.message.chat_id,
                    text="Help!")


class ChatModule(object):
    def __init__(self, store):
        self.handlers = [
            MessageHandler([Filters.text], self.message)
        ]

        self.store = store

    @run_async
    def message(self, bot, update):
        bot.sendMessage(update.message.chat_id,
                        text=update.message.text)

    def get_handlers(self):
        return self.handlers
