import re

celcova_cena = '11 294 800 Kč (440 000 EUR) za nemovitost, včetně provize (k jednání)'
price_list = re.findall(r'\d+', celcova_cena)
letters = []
for i in celcova_cena:
    letters.append(i)
price_str = ''
counter = 0
flag = True
for i in letters:
    if i == '(':
        flag = False
    if i == ')':
        flag = True
    if i.isdigit() and flag:
        price_str = price_str + i
print(price_str)
price_int = int(price_str)
