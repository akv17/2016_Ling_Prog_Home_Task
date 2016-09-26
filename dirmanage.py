import os

d = {'one': 1, 'two': 2, 'three': 3}


def wr(x, y):
    f = open(y + '\\' + 'value.txt', 'w')
    f.write(str(x))
    f.close()
    
    return 0
    
for el in d:
    p = 'C:\\Users\\student\\Desktop\\test\\' + el
    if not os.path.exists(p):
        os.makedirs(p)
        wr(d[el], p)

print('done') 
