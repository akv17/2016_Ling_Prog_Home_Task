import flask
import telebot  
import rhm_ng as rhm
import mrph
import re
import random
import os


TOKEN = os.environ['RTOKEN']

bot = telebot.TeleBot(TOKEN, threaded=False)

bot.remove_webhook()
bot.set_webhook(url='https://akv17-rhymebot-app.herokuapp.com/bot')

app = flask.Flask(__name__)


# set global dict for mrph
global wd
wds = open('dictr.txt', 'r', encoding='utf-8').read().split()
wd = mrph.build_dict(wds)

# info strings
start_inf = open('start_info.txt', 'r', encoding='utf-8').read()
help_inf = open('help_info.txt', 'r', encoding='utf-8').read()


# funcs
kb_remove = telebot.types.ReplyKeyboardRemove(selective=False)


def set_kb():
    kb = telebot.types.ReplyKeyboardMarkup(row_width=2)
    btn1 = telebot.types.KeyboardButton('Да!')
    btn2 = telebot.types.KeyboardButton('Нет.')
    kb.add(btn1, btn2)
    return kb


def w_fix(w):
    return re.sub('[\W]|[0-9]', '', w)


def parse_input(s):
    def check_in(s):
        if not re.search('[\w]', re.sub('\!d|-g|-m|-r|[0-9]', '', s)):
            return -1
        if re.search('[a-zA-Z]', re.sub('\!d|-g|-m|-r|[0-9]', '', s)):
            return 0
        else:
            return True
    
    def report(keys):
        #templ = '%s;%s'
        out = list()
        
        if '-r' in keys:
            r = (True, [])
        else:
            r = (False, [])
            
        # if to morph-transform
        if '-m' in keys:
            m = (True, re.findall('\!d|-g', s))
        else:
            m = (False, [])
        
        out.append(r)
        out.append(m)
        return out
    
    status = check_in(s)
    if status == True:
        keys = re.findall('\!d|-g|-m|-r', s)
        rprt = report(keys)

        splt = [w for w in re.sub('\!d|-g|-m|-r|[0-9]', '', s).split() \
                if re.search('[\w]', re.sub('[\W]', '', w))]
        
        trgt = w_fix(splt[-1])
        if not re.search('[\w]', re.sub('[\W]', '', trgt)):
            return 'badpunct'
        sent = splt[:-1]
        
        # if to capitalize target in respond
        if trgt[0].isupper():
            cap = True
        else:
            cap = False
            
        return trgt.lower(), sent, rprt, cap
    else:
        if status == -1:
            return 'badinp'
        else:
            return 'badlang'      
        

def build_resp(true, rhms, rprt):
    def build_rhms_list(lst):
        res = 'Список рифм:\n'
        for el in lst:
            res += el[0] + ', ' + ', '.join(list(map(str, el[1]))) + '\n'
        return '\n'+res
    
    rhm = random.choice(rhms)[0]
    if rprt[3]:
        rhm = rhm.capitalize()
        
    if rprt[2][1][0] == True:
        # защита от неадекватных сценариев ввода
        # mrph в целом способен справляться с такими случаями
        # тем не менее, возможное всякое
        # срабатывание exception ветки крайне маловероятно
        # если сработала, используется предложение юзера
        try:
            sent_out = mrph.transform(''.join(rprt[2][1][1])+' '+' '.join(rprt[1])+' '+rhm.lower())
        except:
            sent = ' '.join(rprt[1])
            morph = ''
            
        # check if morph-analisis returned
        if '|' in sent_out:
            sent = ' '.join(sent_out.split('|')[0].split()[:-1])
            morph = '\nГрамм. информация:'+sent_out.split('|')[1]
        else:
            sent = ' '.join(sent_out.split()[:-1])
            morph = ''
    else:
        sent = ' '.join(rprt[1])
        morph = ''
        
    # if not returning rhymes list
    if rprt[2][0][0] != True:
        resp = '%s %s %s' % (sent, rhm+'\n', morph)
    else:
        rl = build_rhms_list(rhms)
        resp = '%s %s %s %s' % (sent, rhm+'\n', rl, morph)
    
    return resp


# bot logic
@bot.message_handler(commands=['start', 'help'])
def inf(message):
    if 'start' in message.text:
        bot.send_message(message.chat.id, start_inf)
    else:
        bot.send_message(message.chat.id, help_inf)
    return

@bot.message_handler(func=lambda m: True)
def resp(message):
    global true
    global parsed
    
    if message.text != 'Да!' and message.text != 'Нет.':
        parsed = parse_input(message.text)
        if parsed == 'badinp':
            bot.send_message(message.chat.id, 'Пожалуйста, убедитесь в том, что ваш ввод корректен и попробуйте заново.', 
                         reply_markup=kb_remove)
            return
        elif parsed == 'badlang':
            bot.send_message(message.chat.id, 'Ваш ввод содержит символы латиницы.\n'+
                                           'Этот бот работает только с русским языком.\n'+
                                           'Пожалуйста, следуйте правилам.\n'+
                                           'Чтобы ознакомиться с правилами, воспользуйтесь /help.',
                         reply_markup=kb_remove)
            return
        elif parsed == 'badpunct':
            bot.send_message(message.chat.id, 'Ваш ввод некорректен.\nОбратите внимание на знаки препинания: между ними и словами (особенно последним) не должно быть пробелов.', 
                             reply_markup=kb_remove)
            return
        else:
            true = w_fix(parsed[0])
    
    if message.text == 'Да!':
        # защита от в крайней степени неадекватного ввода
        # хоть и rhm_ng способен отфильтровать и предупредить
        # о таких вводах, всякое может быть и все сценарии
        # неадекватных вводов предусмотреть сложно
        # срабатывание exception ветки крайне маловероятно 
        try:
            res = rhm.rhyme_engine(true, 100, 4, 2)
        except:
            bot.send_message(message.chat.id, 'Что-то пошло не так...\nПожалуйста, убедитесь в том, что ваш ввод корректен и попробуйте заново.', reply_markup=kb_remove)
            return
        if res != -1:
            bot.send_message(message.chat.id, build_resp(true, res, parsed), reply_markup=kb_remove)
            return
        else:
            bot.send_message(message.chat.id, 'По вашему запросу "'+true+'" ничего не найдено.', reply_markup=kb_remove)
            return
    elif message.text == 'Нет.':
        bot.send_message(message.chat.id, 'Выход...\nПо вашему запросу "'+true+'" ничего не найдено.', reply_markup=kb_remove)
        return
    
    else:
        # аналогичная защита от неадек. ввода
        try:
            res = rhm.rhyme_engine(true, 100, 4, 1)
        except:
            bot.send_message(message.chat.id, 'Что-то пошло не так...\nПожалуйста, убедитесь в том, что ваш ввод корректен и попробуйте заново.', reply_markup=kb_remove)
            return
        if res == 0:
            bot.send_message(message.chat.id, 'По вашему запросу "'+true+'" ничего не найдено.\n'+
                                               'Желаете ли вы продолжить поиск рифмы с помощью онлайн-генератора рифм?\n'+
                                               'Выберите соответствующий вариант:\n'+
                                               '- "Да!" - продолжить\n'+
                                               '- "Нет." - выход'
                             , reply_markup=set_kb())
            return
        else:
            bot.send_message(message.chat.id, build_resp(true, res, parsed), reply_markup=kb_remove)
            return
    return


# run web
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return start_inf+'<br><br>'+help_inf

@app.route('/bot', methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)
    
if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
