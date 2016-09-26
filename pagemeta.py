import urllib.request as ur
import re

rawp = ur.urlopen('http://vechorka.ru/article/vybory-na-stavropole-v-obschem-trende/')
p = rawp.read().decode('UTF-8')

def infop(x):
    tit = re.findall('<title>(.*?)</title', x)
    auth = re.findall('author"[\s]*>(.*?)</a>', x)
    date = re.findall('pubdate.*datetime="(.*?)">', x)
    tags = re.findall('href="/tags/.*/">(.*?)</a>', x)
    print(tags)
    
infop(p)
