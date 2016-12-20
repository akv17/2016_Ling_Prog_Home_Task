import re
import os


def get_f():
    f = open('t_main.txt', 'r').read().split()
    return f


## parsing output sql-insert series
def parse(lems, txt_db):
    lem_inf = 'INSERT INTO word_db (id, token, lemma) VALUES ("%s", "%s", "%s");\n'
    txt_db_inf = 'INSERT INTO text_db (token, punct_left, punct_right, text_index, parsed_id) VALUES ("%s", "%s", "%s", "%s", "%s");\n'

    fout = open('sql_out.txt', 'w', encoding='UTF-8')

    for i in range(len(lems)):
        fout.write(lem_inf % (str(i+1), lems[i][0], lems[i][1]))

    fout.write('\n\n')

    for el in txt_db:
        fout.write(txt_db_inf % (el[0], el[1], el[2], el[3], el[4]))

    fout.close()

    return 0


def stem(wds):

    ## a func to return parse_ind value
    def get_prs_ind(wd):
        for i in range(len(lem_lst)):
            if wd == lem_lst[i][0]:
                return i+1

    lem_set = set()

    cur_f = open('help_f.txt', 'w', encoding='UTF-8')
    cur_f.write('\n'.join(wds))
    cur_f.close()

    os.system(r'C:\Users\Artem\Desktop\mystem.exe -nd help_f.txt stem_out.txt')

    ## writing mystem output
    stem_parse = open('stem_out.txt', 'r', encoding='UTF-8').read().split()

    ## parsing lemms table 
    for el in stem_parse:
        res = re.search('{(.*?)}', el)
        if res != None:
            if '|' in res.groups(1)[0]:
                lem_set.add((el.split('{')[0].lower(), res.groups(1)[0].split('|')[0]))
            else:
                lem_set.add((el.split('{')[0].lower(), res.groups(1)[0]))
        else:
            print(el)
            continue

    lem_lst = list(lem_set)

    text_tab_db = []
    ind = 0

    ## parsing text_info table
    for t in range(len(wds)):
        if re.search('[\w]', wds[t]) != None:
            ind += 1
            if t > 0:
                punct_l = re.sub('[\w]', '', wds[t-1])
                if punct_l != '':
                    punct_l = punct_l.split()[-1]
            else:
                punct_l = ''
            punct_r = re.sub('[\w]', '', wds[t])
            tkn = re.sub('[\W]', '', wds[t])
            prs_ind = get_prs_ind(tkn.lower())
            text_tab_db.append((tkn, punct_l, punct_r, str(ind), str(prs_ind)))


    return lem_lst, text_tab_db


def main():
    raw_wds = get_f()
    db = stem(raw_wds)
    parse(db[0], db[1])

    return print('done')


main()
