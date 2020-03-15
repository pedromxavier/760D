import telebot as tb

import re
import html
import urllib.request as req

def STATUS_PONTE():
    URL_PONTE = "https://www.ecoponte.com.br/condicoes-da-via"

    PATTERN = r'<tr class=.*?-row><td>.*?<td>(.*?)<td><span class=.*?>\s*(\S*?)\s*</span>'

    answer = req.urlopen(URL_PONTE)

    answer_bytes = answer.read()
    
    answer_html = answer_bytes.decode('utf8')

    matches = re.findall(PATTERN, answer_html, re.DOTALL)

    TEXT = "O tráfego na ponte está *{}* no sentido *{}* e *{}* no sentido *{}*."

    args = []

    for name, status in matches:
        args.append(html.unescape(status))
        args.append(html.unescape(name))

    return TEXT.format(*args)

def NEXT_FRESCAO():
    pass

def FRESCAO_IMG():
    with open(r'static/HORARIO_FRESCAO.jpg', 'rb') as file:
        return file

def START_TEXT(json):
    if tb.Tempo.morning:
        return "Bom dia, Niterói!"
    
    elif tb.Tempo.evening:
        return "Boa tarde, Niterói!"

    else:
        return "Boa Noite, Niterói!"

def UNKNOWN_TEXT(json):
    return "Comando desconhecido `{text}`".format(json)

bot = tb.Bot(debug=True)

bot.START_TEXT = START_TEXT
bot.UNKNOWN_TEXT = UNKNOWN_TEXT

with bot:
    @bot.cmd_handler('ponte')
    @bot.lock_start
    def ponte(self, update, context):
        self.debug('[Ponte]')

        json = self.parse(update, context)

        kw = {
            'chat_id' : json['chat_id'],
            'text'    : STATUS_PONTE(), 
            'parse_mode' : tb.telegram.ParseMode.MARKDOWN,
        }

        json['bot'].send_message(**kw)

    @bot.cmd_handler('frescao')
    @bot.lock_start
    def frescao(self, update, context):
        self.debug('[Frescão]')

        json = self.parse(update, context)

        kw = {
            'chat_id'    : json['chat_id'],
            'photo'      : FRESCAO_IMG(),
        }

        json['bot'].send_photo(**kw)

if __name__ == '__main__':
    bot.init()