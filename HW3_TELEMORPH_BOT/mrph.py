from pymorphy2 import MorphAnalyzer
from pymystem3 import Mystem
import re
import random


def w_fix(w):
    if re.search('[а-яА-Яеё]', w) != None and re.search('[0-9]', w) != None:
        w = re.sub('[0-9]', '', w)

    if re.search('[\w][\W][\w]', w) != None:
        n_s = ''
        for s in w:
            if s != '-' and re.search('[\W]', s) != None:
                continue
            else:
                n_s += s
        return n_s
    else:
        return re.sub('[\W]', '', w)


def normal(x):
    return x[0].normal_form


def parse(w, if_ambg):
    """return list of parsed-objects with top prob score"""
    #if re.search('[0-9]', w) != None:
    #    print(morph.parse(w))
    if if_ambg:
        ts = morph.parse(w)
        res = list()
        res.append(ts[0])
        if len(ts) > 1:
            top_scr = ts[0].score
            res.extend([t for t in ts[1:] if t.score == top_scr])
        return res
    return morph.parse(w)


def get_rand(x):
    return random.choice(list(wd[x]))


def get_pos(x, if_join):
    """x -- pymorph parse-object"""
    if if_join:
        if x[0].tag.POS == None:
            return '%s %s' % (x[0].word, str(x[0].tag).split(',')[0])
        return '%s %s' % (normal(x), str(x[0].tag.POS))
    else:
        if x[0].tag.POS == None:
            return str(x[0].tag).split(',')[0]
        return str(x[0].tag.POS)


def build_dict(lst):
    global wd
    wd = dict()
    for w in lst:
        try:
            el = get_pos(parse(w_fix(w.split('\n')[0]), False), True)
            if wd.get(el.split()[1]) == None:
                wd[el.split()[1]] = set()
            wd[el.split()[1]].add(el.split()[0])
        except:
            #print(parse(w_fix(w.split('\n')[0])))
            print(w.split('\n'))

    return wd


def parse_input(s, if_underlying):
    global warns
    warns = list()

    def underlying(l):
        res = list()
        for el in l:
            if re.search('[\w]', el) != None:
                res.append(el)
        return res

    def morph_parse(s):
        d = dict()
        for i in range(len(s.split())):
            if re.search('[\W]', s.split()[i]) != None and re.search('[\w]', s.split()[i]) == None:
                continue
            else:
                d[i+1] = list()
                for t in parse(w_fix(s.split()[i]), True):
                    warns.append(t.normal_form)
                    d[i+1].append(str(t.tag)+','+t.word+','+t.normal_form)
        return d

    d = morph_parse(s)
    if if_underlying:
        return underlying(mstm.lemmatize(s)), d
    return [], d


def inflect_it(t):
    flag = False
    n = 0
    t = ''.join(t)
    #print(t)
    if re.split(' |,', t)[0] == 'UNKN':
        return re.split(' |,', t)[-2]

    while flag == False:
        n += 1
        try:
            w_in = get_rand(re.split(' |,', t)[0])
        except:
            #unknown POS-key
            return re.split(' |,', t)[-2]

        w_out = parse(w_in, False)[0].inflect(frozenset(re.split(' |,', t)[1:-2]))
        if w_out != None and w_out.normal_form not in warns:
            # check for not the same random word as inputed
            flag = True
            return w_out.word
        else:
            if n >= 10**3:
                return re.split(' |,', t)[-2]
            continue


def build_resp(d, underl):
    def check_gr(x, n):
        for el in x:
            if el.split(',')[-1] == underl[n-1]:
                return el
        return x[0]

    res = list()
    grs = list()

    n = 0
    for k in d:
        n += 1
        if len(d[k]) < 2:
            res.append(inflect_it(d[k]).strip())
            grs.append(d[k])
        else:
            if len(underl) > 0:
                res.append(inflect_it(check_gr(d[k], n)).strip())
                grs.append(check_gr(d[k], n))
            else:
                res.append(inflect_it(d[k][0]).strip())
                grs.append(d[k][0])

    return res, grs


def transform(s):
    """Transform string 's' into randomized one following original morphological structure.
        You may want to use some of the following options:
        - Use '!d' key before input string for disabling disambiguation (faster)
        - Use '-g' key before input string to get the list of morpho-tags for each word inputed
        Please separate the keys with the space.
        e.g. '!d кот видит собак', '!d-g мама мыла раму'"""
    if re.search('!d', s) == None:
        deep, inpt = parse_input(re.sub('\!d|d|-g|g', '', s), True)
    else:
        deep, inpt = parse_input(re.sub('\!d|d|-g|g', '', s), False)

    resp, grs = build_resp(inpt, deep)
    if re.search('-g', s) != None:
        gr_inf = ''
        res = list()

        res.append(' '.join(resp).capitalize()+'\n')
        for g in grs:
            if type(g) == list:
                res.append(', '.join(g))# + '\n')
            else:
                res.append(', '.join(g.split(',')))# + '\n'
        #return ' '.join(resp).capitalize() + '\n' + gr_inf
        return '\n'.join(res)
    else:
        return ' '.join(resp).capitalize()


def get_dict(path, n):
    return open(path, 'r', encoding='utf-8').read().split('\t')[1:n]

morph = MorphAnalyzer()
mstm = Mystem()
