import re
import os

def get_f():
    f = open('page.html', 'r', encoding='UTF-8').read()
    return f

def task1(f):

    wds_lst = tuple(open('words.txt', 'r', encoding='UTF-8').read().split())
    wds_out = set()
    
    def wd_fix(wd):
        return re.sub('[\W]', '', wd)

    def wd_lst_search(wd):
        for el in wds_lst:
            if wd == el:
                wds_out.add(wd)
        return 0
    
    heads = re.findall('<p>(.*?)</p>', f, flags=re.DOTALL)
    coms = re.findall('class="screen-reader-text">(.*?)</span>', f, flags=re.DOTALL)

    for ln in heads:
        for wd in ln.split():
            wd_lst_search(wd_fix(wd).lower())

    for ln in coms:
        for wd in ln.split():
            wd_lst_search(wd_fix(wd).lower())
            
    f_out = open('wordlist.txt', 'w', encoding='UTF-8')
    for el in wds_out:
        f_out.write(el + '\n')
    f_out.close()

    print(str(len(wds_out)) + ' unparsed words found')
        
    return print('Task 1 done\n')


def task2():
    os.system(r'C:\Users\student\Desktop\mystem.exe -nid words.txt stem_out.txt')
    f_out = open('rus_nouns.txt', 'w', encoding='UTF-8')
    out = set()
    
    f = set(open('stem_out.txt', 'r', encoding='UTF-8').read().split())
    for ln in f:
        res = re.search('(=S.*?=им,ед.*?)', ln, flags=re.DOTALL)
        if res != None and '?' not in ln.split('{')[1].split('=')[0]:
            out.add(ln.split('{')[0])

    for el in out:
        f_out.write(el + '\n')
    f_out.close()

    print(str(len(out)) + ' rus nouns found')

    print('Task 2 done\n')
    
    return out


def task3():
    os.system(r'C:\Users\student\Desktop\mystem.exe -nd rus_nouns.txt stem_nouns_out.txt')
    f = set(open('stem_nouns_out.txt', 'r', encoding='UTF-8').read().split())
    f_out = open('sql.txt', 'w', encoding='UTF-8')

    inf = 'INSERT INTO rus_words (wordform, lemma) VALUES ("%s", "%s");\n'
    
    for el in f:
        wdform = el.split('{')[0]
        lem = el.split('{')[1].rstrip('}')
        if '|' in lem:
            for lm in lem.split('|'):
                f_out.write(inf % (wdform, lm))
        else:
            f_out.write(inf % (wdform, lem))
            
    f_out.close()

    return print('Task 3 done\n')
    
    
    


def main():
    w_page = get_f()
    
    task1(w_page)
    task2()
    task3()
    
    return 0

main()    
