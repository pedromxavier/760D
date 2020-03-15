from telegram.ext import CommandHandler, MessageHandler, Filters, Updater

import telegram

from functools import wraps

import os
import pickle
import datetime as dt

def kwget(key, kwargs, default=None):
    try:
        return kwargs[key]
    except KeyError:
        return default

class _Tempo(object):

    __ref__ = None

    def __new__(cls):
        if cls.__ref__ is None:
            cls.__ref__ = object.__new__(cls)
        return cls.__ref__

    @property
    def hms(self):
        now = dt.datetime.now()
        return (now.hour, now.minute, now.second)

    @property
    def now(self):
        return dt.datetime.now()

    @property
    def morning(self):
        return 5 <= self.now.hour < 12

    @property
    def evening(self):
        return 12 <= self.now.hour < 21

    @property
    def night(self):
        return not (self.morning or self.evening)

Tempo = _Tempo()

class TelegramError(SystemError):
    pass

class Chat:

    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.started = False

        self.data = {}

class Bot:
    """ Interface for building Telegram Bots, built upon the python-telegram-bot extension module.

        Example:
        bot = Bot()
        bot.init()
    """

    @staticmethod
    def START_TEXT(json):
        return "Hello World!"

    @staticmethod
    def UNKNOWN_TEXT(json):
        return "Unknown command `{text}`.".format(**json)

    @staticmethod
    def parse_context(context):
        return {
            'bot' : context.bot
        }

    @staticmethod
    def parse_update(update):
        return {
            'chat_id' : update.message.chat_id,
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
        self.__debug = kwget('debug', kwargs, False)

        self.handlers = []
        self.chats = {}

    def debug(self, *args, **kwargs):
        if self.__debug: return print(*args, **kwargs)

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

    def build(self):
        self.updater = Updater(self.token, use_context=True)

        self.dispatcher = self.updater.dispatcher

        self.add_handlers()

    def init(self):
        self.debug('[Init]')

        ## Build Handlers
        self.debug('    [Build]')
        self.build()

        ## Setup Polling
        self.debug('    [Start Polling]')
        self.updater.start_polling()
        self.updater.idle()

    def __enter__(self):
        self.init_open()

    def __exit__(self, *args):
        self.init_close()

    def init_open(self):
        """
        """
        ## Default /start command
        @self.cmd_handler('start')
        def start(self, update, context):
            self.debug('[Start]')

            json = self.parse(update, context)

            self.debug('    [json]\n{}'.format(json))

            if self.started(json):
                self.debug('    [Already Started for {}]'.format(json['chat_id']))
                return
            else:
                self.debug('    [Starting for {}]'.format(json['chat_id']))
                self.chats[json['chat_id']] = Chat(json['chat_id'])

            kw = {
                'chat_id'    : json['chat_id'],
                'text'       : self.START_TEXT(json),
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
            self.debug('[Unknown]')

            json = self.parse(update, context)

            self.debug('    [json]\n{}'.format(json))

            kw = {
                'chat_id'    : json['chat_id'],
                'text'       : self.UNKNOWN_TEXT(json),
                'parse_mode' : telegram.ParseMode.MARKDOWN,
            }

            json['bot'].send_message(**kw)


    def started(self, json):
        return (json['chat_id'] in self.chats) and (self.chats[json['chat_id']].started)

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

    def run(self):
        try:
            self.init()
        except KeyboardInterrupt:
            pass
        except:
            raise
        finally:
            self.dump()

    @property
    def token(self):
        return self.__load_token()

    @staticmethod
    def __load_token():
        from dotenv import load_dotenv
        
        load_dotenv()

        return os.getenv("TELEGRAM_TOKEN")