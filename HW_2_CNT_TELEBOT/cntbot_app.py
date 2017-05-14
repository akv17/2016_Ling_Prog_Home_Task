import telebot
import conf
import flask
import re

WEBHOOK_URL_BASE = "https://{}:{}".format(conf.WEBHOOK_HOST, conf.WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(conf.TOKEN)

bot = telebot.TeleBot(conf.TOKEN, threaded=False)

bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH)

app = flask.Flask(__name__)

regexp = re.compile('[\W]|[0-9]')
def fix_text(t):
    return re.sub(regexp, ' ', t)

@bot.message_handler(commands=['start', 'help'])
def rpl_wlcm(message):
    bot.send_message(message.chat.id,
                     'Hi! This a bot that is able to count' \
                     ' the number of word-tokens in your message, '\
                     'which means that digits are not treated as such.')
    return

@bot.message_handler(func=lambda m: True)
def rpl_len(message):
    tmpl = 'There %s %s word-token%s in your message.'
    l = len(fix_text(message.text).split())
    if l < 1:
        l = 'no'
        vrb = 'are'
        sfx = 's'
    elif l > 1:
        vrb = 'are'
        sfx = 's'
    else:
        vrb = 'is'
        sfx = ''

    bot.send_message(message.chat.id, tmpl%(vrb, l, sfx))
    return

@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'running'

@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)
