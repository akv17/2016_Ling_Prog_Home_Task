import urllib.request as ur
import re

def op():
    f = ur.urlopen('http://vechorka.ru/')
    t = f.read().decode('UTF-8')
    return t

def regx(x):
    m = re.findall('<h[\d]><a href="/[article|news].+?>(.*?)</a>', x)
    return m

def main():
    fout = open('*path*', 'w')
    var = op()
    var2 = regx(var)
    for el in var2:
        fout.write(el + '\n')
    fout.close()
    return print('done')

main()
