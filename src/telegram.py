from telegram.ext import CommandHandler, MessageHandler, Filters, Updater

import telegram

from functools import wraps

import os
import pickle
import datetime as dt

class TelegramError(SystemError):
    pass

class Chat:

    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.started = False

        self.data = {
            'sent_msgs' : []
        }

class Bot:
    """ Interface for building Telegram Bots, built upon the python-telegram-bot extension module.

        Example:
        bot = Bot()
        bot.init()
    """

    START_TEXT = "Hello!"

    UNKNOWN_TEXT = "Unknown command `{text}`."

    @staticmethod
    def parse_context(context):
        return {
            'bot' : context.bot
        }

    @staticmethod
    def parse_update(update):
        return {
            'chat_id' : update.chat_id,
            'date'    : update.message.date,
            'msg'     : update.message,
            'text'    : update.message.text,
            'audio'   : update.message.audio,
            'video'   : update.message.video,
            'voice'   : update.message.voice,
        }

    @staticmethod
    def parse(update, context):
        json = {}
        json.update(Bot.parse_update(update))
        json.update(Bot.parse_context(context))
        return json

    @staticmethod
    def lock_start(callback):
        @wraps(callback)
        def new_callback(self, update, context):
            json = self.parse(update, context)

            if self.started(json):
                return callback(self, update, context)
            else:
                return
        return new_callback

    def __init__(self, *arg, **kwargs):
        self.handlers = []
        self.chats = {}

    def cmd_handler(self, cmd, **kwargs):
        def decor(callback):
            handler = CommandHandler(cmd, lambda update, context: callback(self, update, context), **kwargs)
            self.handlers.append(handler)
            return handler 
        return decor 

    def msg_handler(self, msg, **kwargs):
        def decor(callback):
            handler = MessageHandler(msg, lambda update, context: callback(self, update, context), **kwargs)
            self.handlers.append(handler)
            return handler 
        return decor

    def add_handlers(self):
        for handler in self.handlers:
            self.dispatcher.add_handler(handler)

    def init(self):
        self.init_open()

        self.updater = Updater(self.token, use_context=True)

        self.dispatcher = self.updater.dispatcher

        self.add_handlers()

        self.init_close()

        ## Setup Polling
        self.updater.start_polling()
        self.updater.idle()

    def init_open(self):
        """
        """
        ## Default /start command
        @self.cmd_handler('start')
        def start(self, update, context):
            json = self.parse(update, context)

            if self.started(json):
                return
            else:
                self.chats[json['chat_id']] = Chat(json['chat_id'])

            kw = {
                'chat_id'    : json['chat_id'],
                'text'       : self.START_TEXT.format(**json),
                'parse_mode' : telegram.ParseMode.MARKDOWN,
            }

            json['bot'].send_message(**kw)

            self.chats[json['chat_id']].started = True

    def init_close(self):
        """
        """
        ## Unknown Command
        @self.msg_handler(Filters.command)
        @self.lock_start
        def unknown(self, update, context):
            json = self.parse(update, context)

            kw = {
                'chat_id'    : json['chat_id'],
                'text'       : self.UNKNOWN_TEXT.format(**json),
                'parse_mode' : telegram.ParseMode.MARKDOWN,
            }

            json['bot'].send_message(**kw)


    def started(self, json):
        return json['chat_id'] in self.chats and self.chats[json['chat_id']].started

    @staticmethod
    def load(fname):
        """
        """
        try:
            with open("{}.bot".format(fname), 'rb') as file:
                return pickle.load(file)
        except FileNotFoundError:
            raise TelegramError('Bot file "{}.bot" not found.'.format(fname))

    def dump(self, fname):
        """
        """
        with open("{}.bot".format(fname), 'wb') as file:
            pickle.dump(self, file)

    def main(self):
        try:
            self.init()
        except KeyboardInterrupt:
            pass
        except:
            raise

    @property
    def token(self):
        return self.__load_token()

    @staticmethod
    def __load_token():
        from dotenv import load_dotenv
        
        load_dotenv()

        return os.getenv("TELEGRAM_TOKEN")

    
