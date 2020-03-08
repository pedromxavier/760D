from telegram.ext import CommandHandler, MessageHandler, Filters, Updater

from conf.settings import TOKEN

import datetime as dt

def cmd_handler(cmd, **kwargs):    
    return (lambda callback : CommandHandler(cmd, callback, **kwargs))

def msg_handler(cmd, **kwargs):    
    return (lambda callback : MessageHandler(cmd, callback, **kwargs))


def update_json(update):
    return {
            'chat_id' : update.message.chat_id,
            }

@cmd_handler('start')
def start(bot, update):
    msg = "Bom dia Niterói!"

    json = update_json(update)

    bot.send_message(
            chat_id=json['chat_id'],
            text=msg
            )

@cmd_handler('ponte')
def ponte(bot, update):
    msg = "A ponte tá {}."

    now = dt.datetime.now()

    if 7 <= now.hour <= 11 or 16 <= now.hour <= 19:
        msg = msg.format('ruim')
    else:
        msg = msg.format('boa')

    json = update_json(update)
    
    bot.send_message(
            chat_id=json['chat_id'],
            text=msg
            )

@msg_handler(Filters.command)
def unknown(bot, update):
    json = update_json(update)

    bot.send_message(
            chat_id=json['chat_id'],
            text='?'
            )


def main():
    updater = Updater(token=TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(start)
    dispatcher.add_handler(ponte)
    
    dispatcher.add_handler(unknown)

    updater.start_polling()

    updater.idle()

    
if __name__ == '__main__':
    try:
        print("-- start --")
        main()
    except:
        raise
    finally:
        print("-- finish --")