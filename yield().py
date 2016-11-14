import re

def srch(p, w):
    f = open(p, 'r')
    for ln in f:
        if w.lower() in ln or w.capitalize() in ln:
            curln = ln.split()
            l = len(curln)
            #print(curln)
            for wd in curln:
                if wd == w.lower():
                        ind = curln.index(w.lower())
                        if l - (ind+1) <= 2 and l - (ind+1) >= (l-2):
                            yield(curln[:ind] + ' ' + w.lower() + ' ' + curln[ind+1:])
                            
                        elif l - (ind+1) <= 2 and l - (ind+1) <= (l-2):
                            yield(curln[ind-2:ind] + ' ' + w.lower() + ' ' + curln[ind+1:])
                            
                        elif l - (ind+1) >= 2 and l - (ind+1) >= (l-2):
                            yield(curln[:ind] + ' ' + w.lower() + ' ' + curln[ind+1:ind+3])
                            
                        elif l - (ind+1) >= 2 and l - (ind+1) <= (l-2):
                            yield(curln[ind-2:ind] + ' ' + w.lower() + ' ' + curln[ind+1:ind+3])
                        
                elif wd == w.capitalize():
                    ind = curln.index(w.capitalize())
                    if l - (ind+1) <= 2 and l - (ind+1) >= (l-2):
                            yield(' '.join(curln[:ind]) + ' ' + w.capitalize() + ' ' + ' '.join(curln[ind+1:]))
                            
                    elif l - (ind+1) <= 2 and l - (ind+1) <= (l-2):
                            yield(' '.join(curln[ind-2:ind]) + ' ' + w.capitalize() + ' ' + ' '.join(curln[ind+1:]))
                            
                    elif l - (ind+1) >= 2 and l - (ind+1) >= (l-2):
                            yield(' '.join(curln[:ind]) + ' ' + w.capitalize() + ' ' + ' '.join(curln[ind+1:ind+3]))
                            
                    elif l - (ind+1) >= 2 and l - (ind+1) <= (l-2):
                            yield(' '.join(curln[ind-2:ind]) + ' ' + w.capitalize() + ' ' + ' '.join(curln[ind+1:ind+3]))
                 
                    

for wd in srch('t.txt', 'Болконский'):
    print(wd + '\n')
