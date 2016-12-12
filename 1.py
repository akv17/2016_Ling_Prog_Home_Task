import re
import os

global db_name
db_name = 'word_db'

s = set()

global wset
wset = set()

def wd_op(wd):
    return re.sub(r'\.*|!|\?|"|\'|:|;|\-|\,', '', wd)

def get_f():
    global wset
    f = open('t.txt', 'r').read().split()
    for wd in f:
        wset.add(wd)
    return f

def parse_wd(wds):
    inf = 'INSERT INTO %s (token, lemma) VALUES ("%s", "%s");\n'
    fout = open('out.txt', 'w', encoding='UTF-8')
    for el in wds:
        fout.write(inf % (db_name, el[0], el[1]))
    fout.close()
    return 0

def stem(wds):
    i = 0
    excl = '.,!?:;-"'
    out_set = set()
    
    cur_f = open('help_f.txt', 'w', encoding='UTF-8')
    cur_f.write('\n'.join(wds))
    cur_f.close()
    
    os.system(r'C:\Users\student\Desktop\mystem.exe -n-d-i help_f.txt stem_out.txt')

    stem_parse = open('stem_out.txt', 'r', encoding='UTF-8').read().split()

    for el in stem_parse:
        res = re.search('{(.*?)}', el)
        if res != None:
            i += 1
            if '|' in res.groups(1)[0]:
                out_set.add((el.split('{')[0], res.groups(1)[0].split('|')[0], i))
            else:
                out_set.add((el.split('{')[0], res.groups(1)[0], i))
        else:
            print(el)
            continue

    text_out_set = set()
    
    for t in range(len(wds)):
        for n in out_set:
            if wds[t] == el[0].lower():

                if t != 0:                                                  #lpunct as previous element of the splitted text
                    if wds[t-1] in excl:
                        lpunct = wds[t-1]
                    else:
                        lpunct = ''
                        
                if re.search('(.*?)[\w]', wd) != None:
                    lpunct += re.search('((.*?)[\w])', wd).groups()[1].strip()

                if re.search('[\w]+(.*?)', wd) != None:
                    rpunct = re.search('([\w]+(.*))', wd).groups()[1].strip()
                else:
                    rpunct = ''
                    
                text_out_set.add((wds[t], el[2], lpunct, rpunct)) 
        
    return out_set, text_out_set

def main():
    raw_wds = get_f()                               #all the words
    
    #for el in wset:
     #   print(el)
    out_set = stem(raw_wds)[1]
    print(len(out_set))
    for el in out_set:
        print(el)
    #parse_wd(out_set)
        
    return print('done')
    
main()
