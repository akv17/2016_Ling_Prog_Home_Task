import telebot
import mrph
import conf
import flask


WEBHOOK_URL_BASE = "https://{}:{}".format(conf.WEBHOOK_HOST, conf.WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(conf.TOKEN)

bot = telebot.TeleBot(conf.TOKEN, threaded=False)

bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH)

app = flask.Flask(__name__)

# load a dictionary for mrph
wds = open(r'/home/akv17/mysite/dictr.txt', 'r', encoding='utf-8').read().split()
#wds = mrph.get_dict(*path*, *n*)

# initialize dictionary
wd = mrph.build_dict(wds)

start_inf = 'Hi! This bot will reply you with a random twist of your input' \
            'following its original morphological structure.\n' \
            'Use "\help" to see additional info on operating.'

help_inf = 'Transform input string into randomized one following its original morphological structure.\n' \
            'You may want to use some of the following options:\n' \
        '- Use "!d" key before input string for disabling disambiguation (faster)\n' \
        '- Use "-g" key before input string to get the list of morpho-tags for each word inputed.\n' \
        'Please separate the keys with the space.\ne.g. "!d-g мама мыла раму", "!d кот видит собак"'


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if 'help' in message.text:
            bot.send_message(message.chat.id, help_inf)
    else:
        bot.send_message(message.chat.id, start_inf)
    return


@bot.message_handler(func=lambda m: True)
def send_len(message):
    # execute main programm - mrph
    try:
        resp = mrph.transform(message.text)
    except:
        resp = 'Bad input. Please, try something different.'

    bot.send_message(message.chat.id, resp)

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
