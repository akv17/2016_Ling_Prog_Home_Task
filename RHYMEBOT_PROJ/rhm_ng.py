import urllib.request as ur
from urllib.parse import quote as prs
import re
import random


global ruscorp_templ
ruscorp_templ = 'http://search2.ruscorpora.ru/search.xml?&dpp=%s&spd=1&env=alpha&text=lexgramm&mode=poetic&sort=gr_tagging&ext=10&nodia=1&parent1=0&level1=0&lex1=%s&flags1=rhymed&parent2=0&level2=0&min2=1&max2=1'

global rhmgen_templ 
rhmgen_templ = 'https://rifma-online.ru/rifma/%s'

#global n_docs
#n_docs = 100

global thres
thres = 0.5

rhm_gen_regex = re.compile('data-suffix-len.*?>(.*?)<')
preparse_regexp = re.compile('</a><table(.*)[Все приме|Страницы]')
parse_regexp = re.compile('explain.*?>(.*?)</span>[\W]*<br>')


def w_fix(w):
    return re.sub('[\W]', '', w)


def rhyme_fit(true, test, n):
    """Проверить, рифмуются ли текущие слова.
        Введено некое подобие метрики рифмовки - score.
        Если метрика превышает выбранный порог, то слова признаются рифмующимися.
        Метрика настроена прежде всего на чувствительность к порогу, поэтому она не ограничена сверху - greater-is-better.
        Для порога 0.5 (писал только на 0.5; другие желаемые пороги нужно настраивать индивидуально):
        - совпадение конечого гласного - рифма
        - совпадение конечных согласных + предш. гласных - рифма
        - совпадение ряда (3) согласных - рифма
        - совпадение конечных согласных - не рифма
        - и т.д.
        Коэф. отражают важность позиции (последняя - самая важная и т.п.) и содержатся в соотв. словаре.
        true - слово юзера
        test - тестируемое на рифмовку слово
        n - длина рифмы как гиперпараметр
        Возвращает: bool - рифмуется ли, метрику, acc_score, рифму
        """
    # n - num of symbols to be checked
    #thres = 0.5
    # sovpadenie konechnux glasnyx
    # libo 3 odinakovyx soglasnyx
    def pairwise(true, test, i):
        """Проверить, совпадают ли текущие символы.
        Будем считать совпадение рифмой.
        Есть отдельная ветка для конечных зв/глух. шумных
        true - символ true слова
        test - символ test слова
        i - их индекс (позиция в слове)"""
        
        if true in vocs and test not in vocs:
            return 0
        if true in cons and test not in cons:
            return 0
        else:
            # ветка для гласных
            if true in vocs and test in vocs:
                if true == test:
                    return 0.25
                else:
                    return 0
                
            # ветка для согласных
            elif true in cons and test in cons:
                # ветка для проверки конечных шумных
                if i == -1:
                    if true == test or true == unvoiced(test):
                        return 0.125
                    else:
                        return 0 
                # для неконечных
                else:
                    if true == test:
                        return 0.125
                    else:
                        return 0
            else:
                return 0
            
    def unvoiced(cons):
        """Пара для конечного шумного.
        cons - любой согласный"""
        
        paired = 'бпвфдтзсжшгк'
        if cons in paired:
            return d_unvoiced[cons]
        else:
            return cons
    
    def rhyme_accuracy_score(n, rhyme):
        """Аналог скоринга для полученной рифмы.
        Считает точные символьные совпадения
        n - установленная длина рифмы
        rhyme - полученная рифма"""
        
        if n > len(true):
            n = len(true)
        return round(len(rhyme)/n, 2)

    def get_bound(true, test):
        """Длина наикратчайшего слова из сравниваемых."""
        
        if len(true) > len(test):
            return len(test)
        else:
            return len(true)
        
    vocs = 'июеёэяыауо'
    cons = 'йцкнгшщзхъждлрпвфчсмтьб'
    thres = 0.5
    bound = get_bound(true, test)
    score = 0
    rhyme = ''
    zero_flag = False
    
    # dict of rhyming symbs coef
    d_coef = {-1:2, -2:1.5, -3:1, -4:0.5}
    d_unvoiced = {'б':'п', 'п':'б',
              'в':'ф', 'ф':'в',
              'д':'т', 'т':'д',
              'з':'с', 'с':'з',
              'ж':'ш', 'ш':'ж',
              'г':'к', 'к':'г'}
    
    for i in range(1, n+1):
        if i <= bound:
            i = i*-1
            status = pairwise(true[i], test[i], i)
            if status != 0:
                if zero_flag != True:
                    score += d_coef[i]*status
                    rhyme += test[i]
            else:
                zero_flag = True
        else:
            break
            
    if score >= thres:
        return True, score, rhyme_accuracy_score(n, rhyme), rhyme[::-1]
    else:
        return False, score, rhyme_accuracy_score(n, rhyme), rhyme[::-1]
    

def get_req(url_path, encd):
    try:
        return ur.urlopen(url_path).read().decode(encd)
    except:
        return 'BAD REQUEST' 
    
    
def rhymegen_req(true, n):
    """Получить выдачу онлайн генератора-рифм.
        true - слово юзера
        n - длина выдачи как гиперпараметр"""
    
    req = get_req(rhmgen_templ % (prs(true)), 'utf-8')
    ws = re.findall(rhm_gen_regex, req)
    if len(ws) < n:
        return ws
    else:
        return ws[:n]
    
    
def parse_html(true, p):
    if re.search('По этому запросу ничего не найдено', p):
        return 'RusCorp NOT FOUND'
    else:
        out = list()
        for el in re.findall(preparse_regexp, p):
            for s in re.findall(parse_regexp, el):
                try:
                    w = s.split('>')[-1]
                    if w_fix(w).lower() != true:
                        out.append(w_fix(w).lower())
                except:
                    # bad respond handler
                    continue
        return list(set(out))
    
    
def get_rhymes(true, lst, n):
    """Получить список слов, римующихся с true.
    n - длина рифмы как гиперпараметр"""
    
    d = dict()
    max_scr = 0
    
    for w in lst:
        scr = rhyme_fit(true, w, n)
        if scr[0] == True:
            d[w] = scr[1:]
            if scr[1] > max_scr:
                max_scr = scr[1]
        else:
            continue

    # if no applicable rhyme found
    # including empty RusCorpora respond
    if max_scr < thres:
        return None
    else:
        # 2d array of rhymes with the highest score
        return [[k, d[k]] for k in d if d[k][0] == max_scr]
    
    
def check_respond(true, lst, n):
    if len(lst) > 0:
        return get_rhymes(true, lst, n)
    else:
        return None
    

def get_ruscorp(true, n_docs, n):
    crp_res = parse_html(true, get_req(ruscorp_templ % (n_docs, prs(true)), 'windows-1251'))
    # if not found
    if type(crp_res) == str:
        return [], 0
    
    # return rhymes
    # may also be aborted if thres
    # not passed
    else:
        crp_rhms = check_respond(true, crp_res, n)
        if crp_rhms:
             return crp_rhms, 1
        else:
            return [], 0

        
def get_rhymegen(true, n):
    gen_res = rhymegen_req(true, n)
    
    if len(gen_res) == 0:
        return [], -1
    else:
        gen_rhms = check_respond(true, gen_res, n)
        if gen_rhms:
            return gen_rhms, 1
        else:
            return [], -1
        

def resp_handler(status):
    if status == 0:
        return None
    elif status == -1:
        return None
    else:
        return 1
    
    
def rhyme_engine(true, n_docs, n, flag):
    """Главная ф-ия: строит список рифм, объединяя все процедуры.
       true - слово юзера
       n_docs -- кол-во документов в выдаче НКРЯ; гиперпараметр
       n - длина рифмы как гиперпараметр
       flags: 1 - use RusCorp, 2 - use rhyme-gen"""
    
    # x_res: [0] - list of rhymes, [1] - status
    if flag != 2:
        ruscorp_res = get_ruscorp(true, n_docs, n)
        if resp_handler(ruscorp_res[1]) != 1:
            return 0 # report if nothing found
        else:
            return ruscorp_res[0]
    else:
        gen_res = get_rhymegen(true, n)
        if resp_handler(gen_res[1]) != 1:
            return -1 # report if nothing found
        else:
            return gen_res[0]

