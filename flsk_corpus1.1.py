from flask import Flask, render_template, request, redirect, url_for
import re

app = Flask(__name__)

ld = {}
t_in = open('t.txt', 'r').read()
t = re.split('\.|\?|!', t_in)   
def srch(x):
    rawout = [re.sub('\[|\]|\\n?', '', s.lstrip(' ')) for s in t if x.lower() in s.split() or x.capitalize() in s.split()]
    for s in rawout:
        flag=False
        for el in s:
            if x == el:
                flag=True
                el = el.upper()
        if flag == False:
            rawout.remove(s)
    out = [x.split() for x in rawout]
    return out

@app.route('/')
def sform():
    if 'wd' not in request.args:
        return render_template('fm2.html')
    else:
        curwd = request.args['wd']
        fout = open('2.txt', 'w')
        fout.write(curwd)
        return redirect(url_for('m', word=curwd))

@app.route('/outpt/<word>')
def m(word):
    out = srch(word)
    return render_template('wl2.html', wd1 = word.lower(), wd2 = word.capitalize(), wdl=out)    


if __name__ == '__main__':
    app.run(debug=False)
