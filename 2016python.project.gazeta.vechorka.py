import urllib.request as ur
import re
import os
import time

global sketch
sketch = 'http://vechorka.ru/newspaper/'
global artcnt
artcnt = 0

global rootdir
rootdir = 'C:\\py\\proj\\testdir\\газета' #please set the root needed here
global blockslist
blockslist = ['plain', 'mystem-xml', 'mystem-plain']

regex = re.compile('a.*href="(/[article|news]*/.*/)"')
articlereg = re.compile('<p?P?.*?align.*?"?>(.*?)</p?P?>') 
#newsreg = re.compile('<p.*(<font|class=|style=).*".*>*<*>(.*?)</p>')
headerreg = re.compile('(?<= )<h2>(.*?)</h2>')
namecleanreg = re.compile(r'\\|\/|\:|\*|\?|\"|\<|\>|\|')

def root_dir(): #creating root and meta csv
    if os.path.exists(rootdir) != True:
        os.makedirs(rootdir)
    if os.path.exists(rootdir + '\\metadata.csv') != True:
        metatable = open(rootdir + '\\metadata.csv' , 'w')
        metatable.write('path\tauthor\tsex\tbirthday\theader\tcreated\tsphere\tgenre_fi\ttype\ttopic\tchronotop\tstyle\taudience_age\taudience_level\taudience_size\tsource\tpublication\tpublisher\tpubl_year\tmedium\tcountry\tregion\tlanguage' + '\n')
        metatable.close()
    for el in blockslist:
        if os.path.exists(rootdir + '\\' + el) != True:
            os.makedirs(rootdir + '\\' + el)
        
    return print('rooting done')

def crawl(x): #listing article urls of the newspaper
    try:
        rawp = ur.urlopen(x)
        p = rawp.read().decode('UTF-8')
        articlelist = []
        rawarticlelist = regex.findall(p)
        for el in rawarticlelist:
            if el not in articlelist:
                articlelist.append(el)
        
                
        return articlelist
    
    except:
        print('Bad url --- newspaper:', x)
        return 0

def page_meta_info(x): #getting data for the meta
    
    pagemetaout = []
    
    author = re.findall('author"[\s]*>(.*?)</a>', x)
    for au in author:
        if 'Неизвестный' in au:
            author.remove(au)
        else:
            continue
    if len(author) == 0:
        pagemetaout.append('NoName')
    else:
        pagemetaout.append(', '.join(author))
    title = re.findall('<title>(.*?)</title', x)
    pagemetaout.append(''.join(title))
    date = re.findall('pubdate.*datetime="(.*?)">', x)
    pagemetaout.append(''.join(date).split('T')[0].replace('-', '.'))
    tags = re.findall('"keywords".*content="(.*?)"', x)
    pagemetaout.append(''.join(tags).rstrip(','))
    purl = re.findall('"canonical".*href="(.*?)"', x)
    pagemetaout.append(''.join(purl))

    return tuple(pagemetaout)

def meta_tab(meta, path): #writting meta csv
    tab = open(rootdir + '\\metadata.csv', 'a')
    y = path.split('\\')[-3]
    ppath = rootdir + '\\plain\\' + path
    md = (ppath, meta[0], meta[1], meta[2], meta[3], meta[4], y)
    ln = '%s\t%s\t\t\t%s\t%s\tпублицистика\t\t\t%s\t\tнейтральный\tн-возраст\tн-уровень\tгородская\t%s\tВечёрка\t\t%s\tгазета\tРоссия\tСтаврополь\tru'
    tab.write(ln % md + '\n')
    tab.close()

def name_fix(pagen): #fix the name for the restr symbs
    return re.sub(r'\\|\/|\:|\*|\?|\"|\<|\>|\|', '', pagen)

def get_text(page): #getting plain text here 
    textdata = []
    header = (''.join(headerreg.findall(page)))
    textdata.append(header)
    rawtextdata = articlereg.findall(page)      
    for el in rawtextdata:
        curline = re.sub('("><span lang="ru-RU|<.*?>|&.*?;|\**)', '', el)
        textdata.append(curline.strip())

    return textdata 

def builddir(date): #create dir of the date given
    global rootdir
    global blockslist
    global pagepath
    y = date.split('.')[0] #year
    m = date.split('.')[1].lstrip('0') #month
    pagepath = y + '\\' + m + '\\'
    for el in blockslist:
        if os.path.exists(rootdir + '\\' + el + '\\' + y) != True:
            os.makedirs(rootdir + '\\' + el + '\\' + y)
        if  os.path.exists(rootdir + '\\' + el + '\\' + y + '\\' + m) != True:
            os.makedirs(rootdir + '\\' + el + '\\' + y + '\\' + m)

    return pagepath

def op(page, path, meta): #processing an article
    global artcnt
    pagename = name_fix(meta[1])
    text = '\n'.join(page)
    if text == '':
        print('Bad page structure --- ', meta[4])
        return 0
    else:
        def stem(): 
            hf = open('C:\\py\\stemin.txt', 'w', encoding='UTF-8') #help-file for mystem operating, may be placed wherever
            hf.write(text)
            hf.close()
            stem = os.system('C:\\Users\\Artem\\Desktop\\mystem.exe -nid C:\\py\\stemin.txt C:\\py\\stemout.txt')
            morph = open('C:\\py\\stemout.txt', 'r', encoding='UTF-8').read()
            morphout = open(rootdir + '\\mystem-plain\\' + path + pagename + '.txt', 'w', encoding='UTF-8')
            morphout.write(morph)
            
            stemx = os.system('C:\\Users\\Artem\\Desktop\\mystem.exe -nid --format xml C:\\py\\stemin.txt C:\\py\\stemout.txt')
            morphx = open('C:\\py\\stemout.txt', 'r', encoding='UTF-8').read()
            morphxout = open(rootdir + '\\mystem-xml\\' + path + pagename + '.xml', 'w', encoding='UTF-8')
            morphxout.write(morphx)
            morphout.close()
            morphxout.close()
            
        def plain(page, path, meta):
            fout = open(rootdir + '\\plain\\' + path + pagename + '.txt', 'w', encoding='UTF-8')
            metahead = '@au %s\n@ti %s\n@da %s\n@topic %s\n@url %s\n'
            fout.write(metahead % meta)
            fout.write(text)
            fout.close()
            
            return print(meta[4], ' --- OK')
        
        plain(page, path, meta)
        stem()
        artcnt += 1
        
def get_pages(z): #picks a page from the 'articlelist'
    for el in z:
        try:
            curpage = ur.urlopen('http://vechorka.ru'+el).read().decode('UTF-8')
        
            rawpage = get_text(curpage) #plain text 
            
            curpagemeta = page_meta_info(curpage) #meta data
            curpath = builddir(curpagemeta[2]) #[2] - date of publ
            pars = op(rawpage, curpath, curpagemeta) #provide for plain-stemxml-stemplain
            if pars != 0:
                meta_tab(curpagemeta, curpath)
            
        except:
            print('Bad url --- article:', el)
            continue

def main():
    root_dir()
    tim = 0 #sleep trigger
    for i in range(4900, 6062):
        tim += 1
        if tim > 30:
            time.sleep(300)
            tim = 0
            
        newspaper = crawl(sketch + str(i)) #list of featured articles urls
        print('\n' + sketch + str(i))
        if newspaper != 0:
            get_pages(newspaper) #operating with each article
        else:
            continue
        
    return print(artcnt, 'articles successfully parsed')  

main()
        
    
