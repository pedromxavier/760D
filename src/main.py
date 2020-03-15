from telegram.ext import CommandHandler, MessageHandler, Filters, Updater

from conf.settings import TOKEN

import datetime as dt

def cmd_handler(cmd, **kwargs):    
    return (lambda callback : CommandHandler(cmd, callback, **kwargs))

def msg_handler(cmd, **kwargs):    
    return (lambda callback : MessageHandler(cmd, callback, **kwargs))

class Bot:

    def __init__(bot, *args, **kwargs):
        bot.load()

    def load(bot):
        try:

    def dump(bot):
        pass

    @staticmethod
    def get_json(update, context):
        return {
                'chat_id' : update.message.chat_id,
                'text' : update.message.text,
                'bot' : context.bot
                }

    @cmd_handler('start')
    def start(bot, update, context):
        if bot.STARTED

        msg = "Bom dia Niterói!"

        json = get_json(update, context)

        json['bot'].send_message(
                chat_id=json['chat_id'],
                text=msg
                )

    @cmd_handler('ponte')
    def ponte(bot, update, context):
        msg = "A ponte tá {}."

        now = dt.datetime.now()

        if 7 <= now.hour <= 11 or 16 <= now.hour <= 19:
            msg = msg.format('ruim')
        else:
            msg = msg.format('boa')

        json = get_json(update, context)
        
        json['bot'].send_message(
                chat_id=json['chat_id'],
                text=msg
                )

    @msg_handler(Filters.command)
    def unknown(bot, update, context):
        json = get_json(update, context)

        json['bot'].send_message(
                chat_id=json['chat_id'],
                text='?'
                )

    @msg_handler(Filters.text & Filters.entity('mention'))
    def mention(bot, update, context):
        json = get_json(update, context)

        text = json['text']

        answer = parse(text)

        if answer is not None:
            json['bot'].send_message(
                    chat_id=json['chat_id'],
                    text=answer
                    )

    def main(bot):
        updater = Updater(TOKEN, use_context=True)

        dispatcher = updater.dispatcher

        dispatcher.add_handler(start)
        dispatcher.add_handler(ponte)
        
        dispatcher.add_handler(unknown)

        updater.start_polling()

        updater.idle()

    
if __name__ == '__main__':
    try:
        print("-- start --")
        bot = Bot()
        bot.main()
    except KeyboardInterrupt:
        pass
    except:
        raise
    finally:
        print("-- finish --")