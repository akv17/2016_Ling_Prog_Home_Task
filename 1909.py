import urllib.request as ur
import re

mpage = ur.urlopen('http://www.forumishqiptar.com/forum.php').read().decode('ISO-8859-1')
flist = re.findall('<span class="forumtitle"><a href="(.*?)">', mpage)
thlist = []
for i in range(2):
    print(flist[i])
    thseek = []
    forumpage = ur.urlopen('http://www.forumishqiptar.com/'+flist[i]+'"').read().decode('ISO-8859-1')
    thseek = re.findall('<a href="(.*?)" ', forumpage)
    for el in thseek:
        if 'threads/' in el and 'http' not in el:
            thlist.append(el)

inf = []
for i in range(3):
    num = str(i)
    fout = open(num+'.txt', 'w', encoding='ISO-8859-1')
    thr = ur.urlopen('http://www.forumishqiptar.com/'+thlist[i]+'"').read().decode('ISO-8859-1')
    print(thlist[i])
    text = re.findall('<blockquote.*?>(.*?)<', thr, flags=re.DOTALL)
    for block in text:
        fout.write(block + '\n')
    fout.close()
print('done')    
