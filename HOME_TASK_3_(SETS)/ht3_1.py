import urllib.request as ur
import re
import random

##resource = 'https://news.yandex.ru/yandsearch?lr=213&cl4url=www.m24.ru%2Farticles%2F123576&lang=ru&rubric=science&from=rubric'


l = ['https://iupac.org/iupac-announces-the-names-of-the-elements-113-115-117-and-118/',
     'http://www.rostov.kp.ru/daily/26614.4/3631206/',
     'https://regnum.ru/news/innovatio/2212122.html',
     'http://www.kommersant.ru/doc/3157533',
     'https://ria.ru/science/20161130/1482514345.html',
     'http://tass.ru/info/3827141',
     'https://lenta.ru/news/2016/11/30/nihonium/',
     'http://www.rbc.ru/rbcfreenews/583e9fce9a7947a5fa97062f',
     'https://www.gazeta.ru/science/news/2016/11/30/n_9394913.shtml',
     'http://www.riken.jp/en/pr/topics/2016/20161130_1/',
     'https://lenta.ru/news/2016/11/30/nihonium/',
     'http://www.rostov.kp.ru/daily/26614.4/3631206/',
     'http://www.kommersant.ru/doc/3157533',
     'https://life.ru/939509',
     'http://mir24.tv/news/Science/15378221',
     'http://fedpress.ru/news/77/society/1708229',
     'http://ufacitynews.ru/news/2016/12/01/v-tablice-mendeleeva-oficialno-poyavilis-novye-elementy/',
     'http://ugranow.ru/2016/11/30/%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD-113-%D0%B9-%D1%85%D0%B8%D0%BC%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B9-%D1%8D%D0%BB%D0%B5%D0%BC%D0%B5%D0%BD%D1%82-%D1%82%D0%B0%D0%B1%D0%BB%D0%B8%D1%86%D1%8B/',
     'http://www.ucheba.ru/article/3882']

ver_l = ['lenta', 'tass', 'ugranow', 'ucheba', 'life']

global d
d = {}

global flag
flag = False

global int_wset
int_wset = set()

global sym_wset
sym_wset = set()

global cut
cut = set()

global cap_l
cap_l = set()


##def crawl(x):
##    
##    def filter_for_ru(lst):
##        for el in lst:
##            if re.search('http.*?://.*?\.ru.*?', el) == None:
##                lst.remove(el)
##        return lst
##
##    rawp = ur.urlopen(x)
##    p = rawp.read().decode('UTF-8')
##    res = re.findall('<div class="doc__agency">.*? href="(.*?)" .*?data-counter=', p, flags=re.DOTALL)
##
##    return filter_for_ru(res)
##
###<div class="doc__agency">.*? href="(.*?)" .*?data-counter=
###<div class=".*?agency">.*?[\s]?href="(.*?)"[\s]?.*?data-counter


##def randomize(x):
##    out = []
##    for i in range(5):
##        el = random.choice(x)
##        out.append(el)
##        x.remove(el)
##    return out

def dict_upd(x):
    if x in d:
        d[x] += 1
    else:
        d[x] = 1

    return 0


def get_text(page):
    #print(page)

    def text_fix(t):
        t = re.sub('<.*?>|Подтвердите свой аккаунт.*', '', t, flags=re.DOTALL)
        t = re.sub('&.*?;', ' ', t, flags=re.DOTALL)
        return t
        
    try:
        rawp = ur.urlopen(page)
        p = rawp.read().decode('UTF-8')
    except:
        try:
            p = rawp.read().decode('windows-1251')
        except:
            return print('EXCEPTION\nBAD PAGE: ' + page)
        
    m = re.search('http.*?://(.*?)\.ru', page)
    if m != None:
        pname = m.group(1)
    else:
        pname = 'dull'
    
    for el in ver_l:
        if el in pname:
            content = re.findall('<p>(.*?)</p>', p, flags=re.DOTALL)
            f = open(el + '.txt', 'w')
            f.write(text_fix(' '.join(content)) + '\n')
            f.close()
            return print(pname + ' DONE\n')


def set_func(name):
    global flag
    
    print(name + ' PROCESSING\n') 

    curset = set()
    excl = '().,!?:;-"—№'
    
    def wd_fix(wd):
        return re.sub('\(|\)|\.|\,|\!|\?|\:|\;|\-|—|"|№|»|«', '', wd.strip())
        
    f = open(name + '.txt', 'r').read().split()

    for wd in f:
        if wd not in excl:
            curwd = wd_fix(wd)
            if re.search('[\D]', curwd) != None:
                if curwd[0].isupper() == True:
                    cap_l.add(curwd)
                dict_upd(curwd.lower())
                curset.add(curwd.lower())


    if flag == False:
        flag = True
        int_wset.update(curset)
        sym_wset.update(curset)
    else:
        int_wset.intersection_update(curset)

        curdif = sym_wset.symmetric_difference(curset)
        cut.update(sym_wset.union(curset).difference(curdif))
        sym_wset.symmetric_difference_update(curset)

    curset.clear()
    
    return 0


def upper_func(wd): #func for tracking UPPERCASED words
    trig = False
    for el in cap_l:
        if wd == el.lower():
            trig = True
            return el
    if trig == False:
        return wd

def wr_all():
    global sym_wset
    global cut
    
    fdict = open('dict.txt', 'w')
    for k in d:
        fdict.write(k + ':' + str(d[k]) + '\n')
    fdict.close()

    fint = open('INTERSECT.txt', 'w')
    for wd in sorted(list(int_wset)):
            fint.write(upper_func(wd) + '\n')    
    fint.close()

    sym_wset.difference_update(cut)
    fsym = open('SYM_DIFF.txt', 'w')
    for wd in sorted(list(sym_wset)):
        if d[wd] > 1:
            fsym.write(upper_func(wd) + '\n')#' : ' + str(d[wd]) + '\n')
    fsym.close()

    return print('WRITING DONE\n')
    
def main():
    #data = crawl(resource)
    for block in l:
        if re.search('http.*?://.*?\.ru.*?', block) != None:
            get_text(block)

    for el in ver_l:
        set_func(el)

    wr_all()
    
    return print('ALL DONE')

main()
