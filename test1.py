'''
a = [1, 2, 3]
while True:
    mes = input()
    if mes == '1':
        a.append(4)
    else:
        print(a)
'''
import collections
a = ['spam', 'egg', 'spam', 'counter', 'counter', 'counter']
c = collections.Counter(a)
for el, am in enumerate(c.most_common()):
    print(el, am[0], am[1])