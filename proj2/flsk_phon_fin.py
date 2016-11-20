from flask import Flask, render_template, request, redirect, url_for
import json
import re
import os

app = Flask(__name__)

global n
if os.path.exists('ind.txt') == False:
    f_ind = open('ind.txt', 'w')
    f_ind.write('0')
    f_ind.close()
    
n = int(open('ind.txt', 'r').read().strip())

if os.path.exists('jsndata.txt') == False:
    f_jsn = open('jsndata.txt', 'w')
    f_jsn.close()

if os.path.exists('comments.txt') == False:
    f_com = open('jsndata.txt', 'w')
    f_com.close()

#global jsnd
#jsnd = [] #jsondata storage


def kdict(): #dictionary for resulting tab with keyz as GET_FORM shortcuts and vals as actual tests
    d = {}
    for ln in open('kyz.txt', 'r'):
        d[ln.split(':')[0]] = ln.split(':')[1].rstrip()
    return d

kd = kdict()

def srch_keyz_dict():
    d = {}
    for ln in open('srch-kyz.txt', 'r'):
        d[ln.split(':')[0]] = ln.split(':')[1].rstrip()
    return d

srch_kd = srch_keyz_dict()

def wr(data, n):
    f = open('expdata.txt', 'a', encoding='UTF-8')
    f.write('expid:' + str(n) + '\n')
    data
    for el in data:
        f.write(el + ':' + data[el] + '\n')
    f.write('#\n')
    f.close()
    return 0

def indxing(num):
    f = open('ind.txt', 'w')
    f.write(str(num))
    f.close()

def jsn_upd(data, n):
    f = open('jsndata.txt', 'a')
    f.write('Experiment: ' + str(n) + ';' + json.dumps(data) + '#')
    f.close()
    return 0

def exp_srch(key):
    f = open('expdata.txt', 'r', encoding='UTF-8').read()
    res = re.findall(key+':(.*?)[\s]', f)
    return ';'.join(res)
    
def res_parse():
    out = []
    out.append(exp_srch('expid'))
    sk = open('sktch.txt', 'r')
    for ln in sk: #itering tests
        for k in kd:
            if kd[k] == ln.strip(): #now entering experiment data; KEY as an arg
                out.append(exp_srch(k))
    #print(out) 
    return out

def dict_srch(y, stype):
    out = []
    if stype == 's':
        for el in y:
            for k in kd:
                if k == el:
                    out.append(kd[k])
        return out
    
    else:
        chksum = 0
        for k in srch_kd:
            for el in y.split():
                for wd in srch_kd[k].split():
                    if el.lower().strip() == wd.lower():
                        chksum += 1
                        if chksum == len(y.split()):       
                            return k
        return None
    
    
def srch(x):
    f = open('expdata.txt', 'r', encoding='UTF-8').read()
    stype = x['srch_t']
    itm = x['trgt']
    if stype == 's': #searching for the SOUND
        itm = re.sub('\[|\]', '', itm.strip())
        res = re.findall(r'(.*?):\['+itm+'\][\s]', f) 
        return dict_srch(res, 's'), '['+itm+']'
    else:
        def keyword_check(itm, k):
            for el in k.split():
                if el.lower() in itm.lower():
                    flag = True
                else:
                    return False
            return flag
                
        ky = dict_srch(itm, 'ph')
        #print(ky)
        if ky != None and keyword_check(itm, kd[ky]) == True: 
            res = re.findall(ky+':(.*?)[\s]', f)
        else:
            return [], itm
        return res, srch_kd[ky]

def reqargcheck(z):
    #print(z)
    i = 0
    for k in z:
        if z[k] != '' and '_com' not in k: 
            i += 1
    if i < 13:
        return False
    else:
        return True

def cmnt_wr(x, n):
    f = open('comments.txt', 'a', encoding='UTF-8')
    f.write('Experiment: ' + str(n) + '\n') 
    for k in x:
        if '_com' in k:
            f.write(k + ':' + x[k] + '\n')
    f.write('#\n')
    f.close()
    return 0

    
@app.route('/')
def mform():
    global n
    
    if len(request.args) == 0:
        return render_template('mform.html')
    else:
        feedstat = reqargcheck(request.args) #if a survey is badly passed
        if feedstat == True:
            n += 1
            indxing(n)
            wr(request.args, n)
            jsn_upd(request.args, n)
            cmnt_wr(request.args, n)
        return redirect(url_for('form_msg', status=feedstat))

@app.route('/json')
def jsn():
    return render_template('jform2.html', jsnd=open('jsndata.txt', 'r').read())

@app.route('/stats')
def stform():
    if os.path.isfile('expdata.txt') == True:
        out = res_parse()
        #print(out)
        return render_template('stform2.html', reslst=out)
    else:
        return render_template('errlog.html')
        
@app.route('/search')
def srchform():
    if os.path.isfile('expdata.txt') == True:
        if len(request.args) == 0:
            return render_template('srchform.html')
        else:
            global trgt
            trgt = srch(request.args)
            #print(trgt)
            return redirect(url_for('resform'))
    else:
        return render_template('errlog.html')

@app.route('/results')
def resform():
    return render_template('resform.html', req=trgt[1], trgt=trgt[0])
    

@app.route('/ipa')
def ipachrt():
    return render_template('ipachrt.html')

@app.route('/feed/<status>')
def form_msg(status):
    #print(status)
    if status == 'True':
        return render_template('feed.html')
    else:
        return render_template('badfeed.html')

if __name__ == '__main__':
    app.run(debug=False)
